from __future__ import annotations

import logging
from typing import Any, Callable

from abc import ABC, abstractmethod
from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.types import Baseline

logger = logging.getLogger(__name__)


class BaseBaselineProvider(ABC):
    @abstractmethod
    def get_baseline(
        self, string_id: str, weather: dict[str, Any] | None = None
    ) -> Baseline:
        ...

    @abstractmethod
    def get_baselines(
        self, string_ids: list[str], weather: dict[str, Any] | None = None
    ) -> dict[str, Baseline]:
        ...


class StaticBaselineProvider(BaseBaselineProvider):
    """Fixed-constant baseline; ignores weather.

    Retained as a fallback (used when no weather is available) and for
    backwards compatibility with tests that do not supply weather.
    """

    def __init__(self, config: AlertEngineConfig | None = None) -> None:
        self._config = config or AlertEngineConfig()

    def get_baseline(
        self, string_id: str, weather: dict[str, Any] | None = None
    ) -> Baseline:
        return Baseline(
            string_id=string_id,
            expected_current=self._config.baseline_current,
            expected_voltage=self._config.baseline_voltage,
            expected_power=self._config.baseline_power,
        )

    def get_baselines(
        self, string_ids: list[str], weather: dict[str, Any] | None = None
    ) -> dict[str, Baseline]:
        return {sid: self.get_baseline(sid, weather) for sid in string_ids}


class WeatherAwareBaselineProvider(BaseBaselineProvider):
    """Baseline computed from live irradiance and temperature.

    Expected power/current scale with irradiance (relative to Standard Test
    Conditions) and a temperature coefficient, so a drop in generation caused
    by clouds or night is reflected in the expectation rather than flagged as
    a fault. Voltage is treated as weather-insensitive (nominal). When no
    weather is supplied, falls back to ``StaticBaselineProvider``.
    """

    def __init__(self, config: AlertEngineConfig | None = None) -> None:
        self._config = config or AlertEngineConfig()
        self._fallback = StaticBaselineProvider(self._config)

    def get_baseline(
        self, string_id: str, weather: dict[str, Any] | None = None
    ) -> Baseline:
        if weather is None:
            return self._fallback.get_baseline(string_id)
        return self._baseline_from_weather(string_id, weather)

    def get_baselines(
        self, string_ids: list[str], weather: dict[str, Any] | None = None
    ) -> dict[str, Baseline]:
        return {sid: self.get_baseline(sid, weather) for sid in string_ids}

    def _baseline_from_weather(
        self, string_id: str, weather: dict[str, Any]
    ) -> Baseline:
        irradiance = _coerce_float(weather.get("irradiance")) or 0.0
        temperature = _coerce_float(weather.get("ambient_temperature")) or 25.0

        if irradiance <= self._config.night_irradiance_wpm2:
            expected_power = 0.0
            expected_current = 0.0
            expected_voltage = 0.0  # no PV voltage in the dark
        else:
            irr_factor = irradiance / self._config.stc_irradiance_wpm2
            temp_factor = 1.0 + (self._config.temp_coefficient_pct / 100.0) * (
                temperature - 25.0
            )
            expected_power = self._config.rated_power_per_string_w * irr_factor * temp_factor
            expected_current = self._config.rated_current_a * irr_factor * temp_factor
            expected_voltage = self._config.rated_voltage_v

        return Baseline(
            string_id=string_id,
            expected_current=max(expected_current, 0.0),
            expected_voltage=max(expected_voltage, 0.0),
            expected_power=max(expected_power, 0.0),
        )


class HistoricalBaselineProvider(BaseBaselineProvider):
    """Tier-2 baseline: median power the string historically produced under
    similar weather conditions.

    Queries the telemetry store for past readings with comparable irradiance
    and temperature. When history is thin (fewer than ``min_samples`` matches)
    it degrades gracefully to the ``WeatherAwareBaselineProvider`` physics
    model, so the system self-improves over its first ~2 weeks of data without
    ever being unconfigured. When no weather is supplied it falls back to the
    static baseline via the physics provider.
    """

    def __init__(
        self,
        config: AlertEngineConfig | None = None,
        reading_repo_factory: Callable[[], Any] | None = None,
        physics_provider: WeatherAwareBaselineProvider | None = None,
        min_samples: int = 5,
    ) -> None:
        self._config = config or AlertEngineConfig()
        self._repo_factory = reading_repo_factory or (lambda: None)
        self._physics = physics_provider or WeatherAwareBaselineProvider(self._config)
        self._min_samples = min_samples

    def get_baseline(
        self, string_id: str, weather: dict[str, Any] | None = None
    ) -> Baseline:
        physics_baseline = self._physics.get_baseline(string_id, weather)
        if weather is None:
            return physics_baseline

        repo = self._repo_factory()
        if repo is None:
            return physics_baseline  # no DB available → physics model

        irradiance = _coerce_float(weather.get("irradiance")) or 0.0
        temperature = _coerce_float(weather.get("ambient_temperature")) or 25.0

        # Night → no output expected; physics provider already encodes this.
        if irradiance <= self._config.night_irradiance_wpm2:
            return physics_baseline

        sid = _parse_string_id(string_id)
        if sid is None:
            return physics_baseline  # non-integer id → can't query FK

        try:
            med_power = repo.median_power_for_conditions(sid, irradiance, temperature)
        except Exception:
            logger.debug(
                "Historical baseline query failed for %s; using physics model",
                string_id,
                exc_info=True,
            )
            return physics_baseline

        if med_power is None:
            return physics_baseline  # not enough history yet

        # Scale current proportionally to the learned power vs physics power,
        # so current stays consistent with the empirical expectation.
        if physics_baseline.expected_power > 0:
            ratio = med_power / physics_baseline.expected_power
        else:
            ratio = 0.0
        return Baseline(
            string_id=string_id,
            expected_power=med_power,
            expected_current=physics_baseline.expected_current * ratio,
            expected_voltage=physics_baseline.expected_voltage,
        )

    def get_baselines(
        self, string_ids: list[str], weather: dict[str, Any] | None = None
    ) -> dict[str, Baseline]:
        return {sid: self.get_baseline(sid, weather) for sid in string_ids}


def _parse_string_id(string_id: str) -> int | None:
    """Best-effort extraction of an integer string_id from a Scarda id.

    Scarda uses composite ids like ``SEC01-INV01-STR01``; the DB ``string_id``
    is an integer FK. When the id is purely numeric, return it; otherwise the
    historical provider can't query by FK and falls back to the physics model.
    """
    try:
        return int(string_id)
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

