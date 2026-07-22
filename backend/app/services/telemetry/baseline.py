from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.telemetry.baseline import Baseline
from app.repositories.reading_repository import ReadingRepository


class BaselineService:
    """Manages expected-value baselines per string.

    Baselines represent the ideal (no-fault) operating point and are
    used by the alert engine and the dashboard.  This service lets
    callers set, retrieve, and compute baselines from historical data.
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._reading_repo = ReadingRepository(db)

    async def get_active(self, string_id: int) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        baseline = (
            self._db.query(Baseline)
            .filter(
                Baseline.string_id == string_id,
                Baseline.valid_from <= now,
                (Baseline.valid_until.is_(None) | (Baseline.valid_until >= now)),
            )
            .order_by(Baseline.valid_from.desc())
            .first()
        )
        if baseline is None:
            return None
        return {
            "id": baseline.id,
            "string_id": baseline.string_id,
            "expected_power_w": baseline.expected_power,
            "expected_voltage_v": baseline.expected_voltage,
            "expected_current_a": baseline.expected_current,
            "expected_energy_kwh": baseline.expected_energy,
            "valid_from": baseline.valid_from.isoformat() if baseline.valid_from else None,
            "valid_until": baseline.valid_until.isoformat() if baseline.valid_until else None,
        }

    async def compute_from_history(
        self, string_id: int, hours: int = 168,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=hours)

        avg_current = self._reading_repo.average_current_between(start, now)
        avg_voltage = self._reading_repo.average_voltage_between(start, now)
        avg_power = self._reading_repo.average_power_between(start, now)

        return {
            "string_id": string_id,
            "computed_from_hours": hours,
            "expected_current_a": round(avg_current, 3) if avg_current is not None else None,
            "expected_voltage_v": round(avg_voltage, 1) if avg_voltage is not None else None,
            "expected_power_w": round(avg_power, 2) if avg_power is not None else None,
            "period_start": start.isoformat(),
            "period_end": now.isoformat(),
        }