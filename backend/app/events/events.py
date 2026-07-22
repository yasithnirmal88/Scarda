from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(kw_only=True)
class Event:
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(kw_only=True)
class ReadingGenerated(Event):
    readings: list[dict[str, Any]]
    event_type: str = "reading.generated"
    weather: dict[str, Any] | None = None


@dataclass(kw_only=True)
class ReadingStored(Event):
    string_id: str
    recorded_at: datetime
    event_type: str = "reading.stored"
    voltage: float | None = None
    current: float | None = None
    power: float | None = None
    irradiance: float | None = None
    temperature: float | None = None


@dataclass(kw_only=True)
class AlertCreated(Event):
    alert_id: str
    string_id: str
    alert_type: str
    severity: str
    reason: str
    event_type: str = "alert.created"
    expected_value: float | None = None
    actual_value: float | None = None
    deviation_pct: float | None = None
    raw_alert: dict[str, Any] | None = None


@dataclass(kw_only=True)
class AlertResolved(Event):
    alert_id: str
    string_id: str
    alert_type: str
    event_type: str = "alert.resolved"


@dataclass(kw_only=True)
class WeatherUpdated(Event):
    weather_data: dict[str, Any]
    event_type: str = "weather.updated"


@dataclass(kw_only=True)
class MaintenanceLogged(Event):
    log_id: int | str
    log_data: dict[str, Any]
    event_type: str = "maintenance.logged"


@dataclass(kw_only=True)
class DashboardRefresh(Event):
    event_type: str = "dashboard.refresh"
    reason: str = ""


@dataclass(kw_only=True)
class SchedulerTick(Event):
    tick_type: str
    event_type: str = "scheduler.tick"


EVENT_TYPES = {
    "reading.generated",
    "reading.stored",
    "alert.created",
    "alert.resolved",
    "weather.updated",
    "maintenance.logged",
    "dashboard.refresh",
    "scheduler.tick",
}
