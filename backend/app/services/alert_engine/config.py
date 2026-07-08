from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AlertEngineConfig:
    current_threshold_pct: float = 30.0
    voltage_threshold_pct: float = 15.0
    power_threshold_pct: float = 30.0

    confirmation_cycles: int = 2
    max_confirmation_delay_minutes: int = 20

    severity_warning_threshold: float = 25.0
    severity_critical_threshold: float = 60.0

    enable_recommendations: bool = True

    offline_voltage_threshold: float = 10.0
    offline_current_threshold: float = 0.5

    communication_failure_window_minutes: int = 30

    baseline_current: float = 10.0
    baseline_voltage: float = 820.0
    baseline_power: float = 8200.0

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
