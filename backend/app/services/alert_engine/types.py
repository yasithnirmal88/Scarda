from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AlertState(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Reading(BaseModel):
    string_id: str
    timestamp: datetime
    voltage: float | None = None
    current: float | None = None
    power: float | None = None
    irradiance: float | None = None
    ambient_temperature: float | None = None
    panel_temperature: float | None = None
    status: str = "active"


class Baseline(BaseModel):
    string_id: str
    expected_current: float
    expected_voltage: float
    expected_power: float


class Deviation(BaseModel):
    string_id: str
    current_deviation: float | None = None
    voltage_deviation: float | None = None
    power_deviation: float | None = None
    current_deviation_pct: float | None = None
    voltage_deviation_pct: float | None = None
    power_deviation_pct: float | None = None

    def any_exceed(self, current_thresh: float, voltage_thresh: float, power_thresh: float) -> bool:
        exceeds = False
        if self.current_deviation_pct is not None and abs(self.current_deviation_pct) > current_thresh:
            exceeds = True
        if self.voltage_deviation_pct is not None and abs(self.voltage_deviation_pct) > voltage_thresh:
            exceeds = True
        if self.power_deviation_pct is not None and abs(self.power_deviation_pct) > power_thresh:
            exceeds = True
        return exceeds


@dataclass
class RuleResult:
    triggered: bool
    rule_name: str
    reason: str
    severity: AlertSeverity
    deviation: Deviation | None = None
    expected_value: float | None = None
    actual_value: float | None = None
    deviation_pct: float | None = None


@dataclass
class PendingEntry:
    string_id: str
    rule_name: str
    reason: str
    severity: AlertSeverity
    deviation: Deviation
    first_seen: datetime
    last_seen: datetime
    count: int = 1


class AlertData(BaseModel):
    alert_id: str = Field(default_factory=lambda: "")
    timestamp: datetime
    section: str = ""
    inverter: str = ""
    string: str
    alert_type: str
    expected_value: float | None = None
    actual_value: float | None = None
    deviation_pct: float | None = None
    severity: AlertSeverity
    status: AlertState = AlertState.ACTIVE
    reason: str = ""
    recommendation: str = ""
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: datetime | None = None
    duration_seconds: float | None = None


@dataclass
class AlertSummary:
    total_readings: int = 0
    healthy_readings: int = 0
    pending_alerts: int = 0
    confirmed_alerts: int = 0
    resolved_alerts: int = 0
    average_detection_time: float = 0.0
    detection_times: list[float] = field(default_factory=list)
