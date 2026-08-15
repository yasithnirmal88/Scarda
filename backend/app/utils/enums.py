"""Centralized enum definitions for the application.

All enums used across models, services, and the alert engine are defined here
to ensure a single source of truth and avoid duplicate definitions.
"""

import enum


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    """Return the enum's *values* (not names) for SQLAlchemy ``Enum`` columns.

    SQLAlchemy's ``Enum`` type defaults to using the enum member **name**
    (e.g. ``"OFFLINE"``) as the stored DB value, but our Postgres enum types
    are created from the member **value** (e.g. ``"offline"``). Passing this as
    ``values_callable`` keeps the two in sync so inserts against real
    PostgreSQL/TimescaleDB use the lowercase values the DB expects. SQLite
    (tests) is unaffected.
    """
    return [m.value for m in enum_cls]


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    MANAGER = "manager"


class InverterStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class StringStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertState(str, enum.Enum):
    """Lifecycle states for alerts in the alert engine."""
    PENDING = "pending"
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class MaintenanceStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
