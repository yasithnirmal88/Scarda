from __future__ import annotations

from typing import Any

from abc import ABC, abstractmethod
from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.types import Baseline


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


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

