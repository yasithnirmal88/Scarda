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
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertEngineConfig:
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)