"""Alert engine configuration, bridged from app.config thresholds.

Kept as a dataclass for backward compatibility with the existing
alert engine code.  The ``from_global_settings`` factory populates
values from the unified settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.config import settings


@dataclass
class AlertEngineConfig:
    current_threshold_pct: float = settings.thresholds.CURRENT_THRESHOLD_PCT
    voltage_threshold_pct: float = settings.thresholds.VOLTAGE_THRESHOLD_PCT
    power_threshold_pct: float = settings.thresholds.POWER_THRESHOLD_PCT

    confirmation_cycles: int = settings.thresholds.CONFIRMATION_CYCLES
    max_confirmation_delay_minutes: int = settings.thresholds.MAX_CONFIRMATION_DELAY_MINUTES

    severity_warning_threshold: float = settings.thresholds.SEVERITY_WARNING_THRESHOLD
    severity_critical_threshold: float = settings.thresholds.SEVERITY_CRITICAL_THRESHOLD

    enable_recommendations: bool = settings.thresholds.ENABLE_RECOMMENDATIONS

    offline_voltage_threshold: float = settings.thresholds.OFFLINE_VOLTAGE_THRESHOLD
    offline_current_threshold: float = settings.thresholds.OFFLINE_CURRENT_THRESHOLD

    communication_failure_window_minutes: int = settings.thresholds.COMMUNICATION_FAILURE_WINDOW_MINUTES

    baseline_current: float = settings.thresholds.BASELINE_CURRENT
    baseline_voltage: float = settings.thresholds.BASELINE_VOLTAGE
    baseline_power: float = settings.thresholds.BASELINE_POWER

    # Weather-aware physics-model baseline (Tier 1)
    stc_irradiance_wpm2: float = settings.thresholds.STC_IRRADIANCE_WPM2
    temp_coefficient_pct: float = settings.thresholds.TEMP_COEFFICIENT_PCT
    rated_power_per_string_w: float = settings.thresholds.RATED_POWER_PER_STRING_W
    rated_voltage_v: float = settings.thresholds.RATED_VOLTAGE_V
    rated_current_a: float = settings.thresholds.RATED_CURRENT_A
    night_irradiance_wpm2: float = settings.thresholds.NIGHT_IRRADIANCE_WPM2

    # Tier-2 historical similarity tolerances (Phase 10-12). These make the
    # historical baseline configurable: how close irradiance / temperature /
    # time-of-day must be for a historical sample to count as "similar", how
    # far back to look, and how many matches are required before the empirical
    # median is trusted over the physics model.
    historical_irradiance_band: float = settings.thresholds.HISTORICAL_IRRADIANCE_BAND
    historical_temp_band: float = settings.thresholds.HISTORICAL_TEMP_BAND
    historical_time_of_day_band_hours: float = (
        settings.thresholds.HISTORICAL_TIME_OF_DAY_BAND_HOURS
    )
    historical_lookback_days: int = settings.thresholds.HISTORICAL_LOOKBACK_DAYS
    historical_min_samples: int = settings.thresholds.HISTORICAL_MIN_SAMPLES
    # A reading whose power deviation from the historical median exceeds
    # (mad_multiplier * MAD) AND the power_threshold_pct is treated as an
    # anomaly. MAD is robust to outliers, so a single bad historical sample
    # cannot widen the acceptance band indefinitely.
    historical_mad_multiplier: float = settings.thresholds.HISTORICAL_MAD_MULTIPLIER

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_threshold_pct": self.current_threshold_pct,
            "voltage_threshold_pct": self.voltage_threshold_pct,
            "power_threshold_pct": self.power_threshold_pct,
            "confirmation_cycles": self.confirmation_cycles,
            "max_confirmation_delay_minutes": self.max_confirmation_delay_minutes,
            "severity_warning_threshold": self.severity_warning_threshold,
            "severity_critical_threshold": self.severity_critical_threshold,
            "enable_recommendations": self.enable_recommendations,
            "offline_voltage_threshold": self.offline_voltage_threshold,
            "offline_current_threshold": self.offline_current_threshold,
            "communication_failure_window_minutes": self.communication_failure_window_minutes,
            "stc_irradiance_wpm2": self.stc_irradiance_wpm2,
            "temp_coefficient_pct": self.temp_coefficient_pct,
            "rated_power_per_string_w": self.rated_power_per_string_w,
            "rated_voltage_v": self.rated_voltage_v,
            "rated_current_a": self.rated_current_a,
            "night_irradiance_wpm2": self.night_irradiance_wpm2,
            "historical_irradiance_band": self.historical_irradiance_band,
            "historical_temp_band": self.historical_temp_band,
            "historical_time_of_day_band_hours": self.historical_time_of_day_band_hours,
            "historical_lookback_days": self.historical_lookback_days,
            "historical_min_samples": self.historical_min_samples,
            "historical_mad_multiplier": self.historical_mad_multiplier,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertEngineConfig:
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)