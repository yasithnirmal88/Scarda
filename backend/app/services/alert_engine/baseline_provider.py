from __future__ import annotations

import logging
from datetime import datetime
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
    """Tier-2 baseline: robust expected power the string historically produced
    under similar environmental conditions and time-of-day.

    Algorithm (Phases 10-12):

    1. Filter historical ``StringReading`` rows to the *same string*.
    2. Restrict to a configurable lookback window (default 14 days).
    3. Filter by similar irradiance (+/- ``historical_irradiance_band``).
    4. Filter by similar temperature (+/- ``historical_temp_band``).
    5. Filter by similar time-of-day (+/- ``historical_time_of_day_band_hours``
       of the reference reading's hour), so an 08:00 reading is not compared to
       a 13:00 reading even when irradiance/temperature coincide.
    6. Require at least ``historical_min_samples`` matches.
    7. Expected power = MEDIAN of matching powers (robust central tendency).
    8. Dispersion = MAD (Median Absolute Deviation), robust to outliers; used
       by the alert engine to size the acceptance band and by
       ``explain_reading`` to expose the deviation/score.

    When history is thin (fewer than ``min_samples``) it degrades gracefully to
    the ``WeatherAwareBaselineProvider`` physics model, so the system
    self-improves over its first ~2 weeks of data without ever being
    unconfigured. When no weather is supplied it falls back to the static
    baseline via the physics provider.

    The cloud-vs-fault distinction falls out naturally: a cloud drop lowers
    both the current irradiance AND the historical matches' power, so the
    expected median tracks the actual power -> no deviation -> no alert. A
    degraded string under the same weather produces far less than the
    historical median -> large deviation -> anomaly.
    """

    def __init__(
        self,
        config: AlertEngineConfig | None = None,
        reading_repo_factory: Callable[[], Any] | None = None,
        physics_provider: WeatherAwareBaselineProvider | None = None,
        min_samples: int | None = None,
    ) -> None:
        self._config = config or AlertEngineConfig()
        self._repo_factory = reading_repo_factory or (lambda: None)
        self._physics = physics_provider or WeatherAwareBaselineProvider(self._config)
        self._min_samples = (
            min_samples if min_samples is not None else self._config.historical_min_samples
        )

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

        if irradiance <= self._config.night_irradiance_wpm2:
            return physics_baseline

        sid = _parse_string_id(string_id)
        if sid is None:
            return physics_baseline  # non-integer id → can't query FK

        try:
            stats = self._similarity(repo, sid, irradiance, temperature, weather)
        except Exception:
            logger.debug(
                "Historical baseline query failed for %s; using physics model",
                string_id,
                exc_info=True,
            )
            return physics_baseline

        if stats is None:
            return physics_baseline  # not enough history yet

        med_power = stats["median_power"]
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

    def explain_reading(
        self,
        string_id: str,
        power: float,
        weather: dict[str, Any] | None,
        measured_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Return the full historical-similarity explanation for a reading.

        Exposes everything the frontend needs to explain an anomaly decision:
        current vs expected power, irradiance, temperature, historical sample
        count, historical median, MAD, deviation (% and absolute), an anomaly
        score, and a status string. The frontend never computes these.

        When history is unavailable, reports the physics-model expected power
        with ``historical_sample_count = 0`` and ``status = "insufficient_history"``.
        """
        physics_baseline = self._physics.get_baseline(string_id, weather)
        if weather is None:
            return self._explain_physics(
                string_id, power, physics_baseline, measured_at, "no_weather"
            )

        irradiance = _coerce_float(weather.get("irradiance")) or 0.0
        temperature = _coerce_float(weather.get("ambient_temperature")) or 25.0

        if irradiance <= self._config.night_irradiance_wpm2:
            return self._explain_physics(
                string_id, power, physics_baseline, measured_at, "night"
            )

        sid = _parse_string_id(string_id)
        if sid is None:
            return self._explain_physics(
                string_id, power, physics_baseline, measured_at, "unresolved_id"
            )

        repo = self._repo_factory()
        if repo is None:
            return self._explain_physics(
                string_id, power, physics_baseline, measured_at, "no_database"
            )

        try:
            stats = self._similarity(repo, sid, irradiance, temperature, weather, measured_at)
        except Exception:
            logger.debug("explain_reading query failed for %s", string_id, exc_info=True)
            stats = None

        if stats is None:
            return self._explain_physics(
                string_id, power, physics_baseline, measured_at, "insufficient_history"
            )

        expected = stats["median_power"]
        mad = stats["mad"]
        deviation = power - expected
        deviation_pct = ((power - expected) / expected * 100.0) if expected > 0 else 0.0
        band = self._config.historical_mad_multiplier * mad
        # anomaly_score: how many MADs below the median (0 = at expectation).
        score = (abs(deviation) / mad) if mad > 0 else (abs(deviation_pct) / 100.0)
        is_anomaly = (
            deviation < 0
            and abs(deviation) > band
            and abs(deviation_pct) > self._config.power_threshold_pct
        )
        status = "abnormal" if is_anomaly else "normal"
        return {
            "string_id": string_id,
            "current_power": power,
            "expected_power": round(expected, 2),
            "irradiance": irradiance,
            "temperature": temperature,
            "historical_sample_count": stats["sample_count"],
            "historical_median_power": round(expected, 2),
            "historical_mad": round(mad, 2),
            "deviation": round(deviation, 2),
            "deviation_pct": round(deviation_pct, 2),
            "anomaly_score": round(score, 3),
            "status": status,
            "method": "historical_similarity",
            "reference_at": (measured_at.isoformat() if measured_at else None),
        }

    def _similarity(
        self,
        repo: Any,
        sid: int,
        irradiance: float,
        temperature: float,
        weather: dict[str, Any] | None,
        reference_at: datetime | None = None,
    ) -> dict | None:
        """Call the repo's robust similarity method with configured tolerances.

        Older repos may only implement ``median_power_for_conditions``; in that
        case we wrap the scalar result so this provider keeps working with the
        legacy contract (used by existing unit tests with a fake repo).
        """
        sim = getattr(repo, "similarity_for_conditions", None)
        if callable(sim):
            return sim(
                sid,
                irradiance,
                temperature,
                reference_at=reference_at,
                irradiance_band=self._config.historical_irradiance_band,
                temp_band=self._config.historical_temp_band,
                time_of_day_band_hours=self._config.historical_time_of_day_band_hours,
                lookback_days=self._config.historical_lookback_days,
                min_samples=self._min_samples,
            )
        # Legacy fallback: scalar median only.
        med = repo.median_power_for_conditions(
            sid,
            irradiance,
            temperature,
            irradiance_band=self._config.historical_irradiance_band,
            temp_band=self._config.historical_temp_band,
            lookback_days=self._config.historical_lookback_days,
            min_samples=self._min_samples,
        )
        if med is None:
            return None
        return {
            "sample_count": self._min_samples,
            "median_power": med,
            "mad": 0.0,
            "iqr": 0.0,
            "min_power": med,
            "max_power": med,
            "powers": [med],
        }

    def _explain_physics(
        self,
        string_id: str,
        power: float,
        physics_baseline: Baseline,
        measured_at: datetime | None,
        reason: str,
    ) -> dict[str, Any]:
        expected = physics_baseline.expected_power
        deviation = power - expected
        deviation_pct = ((power - expected) / expected * 100.0) if expected > 0 else 0.0
        return {
            "string_id": string_id,
            "current_power": power,
            "expected_power": round(expected, 2),
            "irradiance": None,
            "temperature": None,
            "historical_sample_count": 0,
            "historical_median_power": round(expected, 2),
            "historical_mad": None,
            "deviation": round(deviation, 2),
            "deviation_pct": round(deviation_pct, 2),
            "anomaly_score": None,
            "status": reason,
            "method": "physics_fallback",
            "reference_at": (measured_at.isoformat() if measured_at else None),
        }


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

