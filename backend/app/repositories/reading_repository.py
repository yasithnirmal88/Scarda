from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.models.telemetry.string_reading import StringReading


class ReadingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, reading: StringReading) -> StringReading:
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def find_by_id(self, reading_id: int) -> StringReading | None:
        return self.db.query(StringReading).filter(StringReading.id == reading_id).first()

    def find_all(self) -> Sequence[StringReading]:
        return self.db.query(StringReading).all()

    def find_by_string(self, string_id: int) -> Sequence[StringReading]:
        return self.db.query(StringReading).filter(StringReading.string_id == string_id).all()

    def find_between(self, start: datetime, end: datetime) -> Sequence[StringReading]:
        return (
            self.db.query(StringReading)
            .filter(StringReading.recorded_at >= start, StringReading.recorded_at < end)
            .all()
        )

    def count_by_string_and_period(
        self, string_id: int, start: datetime, end: datetime
    ) -> int:
        return (
            self.db.query(sa_func.count(StringReading.id))
            .filter(
                StringReading.string_id == string_id,
                StringReading.recorded_at >= start,
                StringReading.recorded_at < end,
            )
            .scalar()
            or 0
        )

    def average_power_between(self, start: datetime, end: datetime) -> float | None:
        result = (
            self.db.query(sa_func.avg(StringReading.power))
            .filter(StringReading.recorded_at >= start, StringReading.recorded_at < end)
            .scalar()
        )
        return float(result) if result is not None else None

    def average_voltage_between(self, start: datetime, end: datetime) -> float | None:
        result = (
            self.db.query(sa_func.avg(StringReading.voltage))
            .filter(StringReading.recorded_at >= start, StringReading.recorded_at < end)
            .scalar()
        )
        return float(result) if result is not None else None

    def average_current_between(self, start: datetime, end: datetime) -> float | None:
        result = (
            self.db.query(sa_func.avg(StringReading.current))
            .filter(StringReading.recorded_at >= start, StringReading.recorded_at < end)
            .scalar()
        )
        return float(result) if result is not None else None

    def total_energy_between(self, start: datetime, end: datetime) -> float:
        avg_power = self.average_power_between(start, end) or 0.0
        hours = (end - start).total_seconds() / 3600.0
        return avg_power * hours / 1000.0

    def peak_power_between(self, start: datetime, end: datetime) -> float | None:
        result = (
            self.db.query(sa_func.max(StringReading.power))
            .filter(StringReading.recorded_at >= start, StringReading.recorded_at < end)
            .scalar()
        )
        return float(result) if result is not None else None

    def reading_count_between(self, start: datetime, end: datetime) -> int:
        return (
            self.db.query(sa_func.count(StringReading.id))
            .filter(StringReading.recorded_at >= start, StringReading.recorded_at < end)
            .scalar()
            or 0
        )

    def median_power_for_conditions(
        self,
        string_id: int,
        irradiance: float,
        temperature: float,
        irradiance_band: float = 100.0,
        temp_band: float = 3.0,
        lookback_days: int = 14,
        min_samples: int = 5,
    ) -> float | None:
        """Median power a string produced under similar conditions.

        Queries historical ``StringReading`` rows for this string within an
        irradiance band (+/- ``irradiance_band``) and a temperature band
        (+/- ``temp_band``) over the last ``lookback_days``. Returns the median
        power, or ``None`` when fewer than ``min_samples`` rows exist (so the
        caller can fall back to the physics model). Used by the Tier-2
        historical baseline.
        """
        start = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        rows = (
            self.db.query(StringReading.power)
            .filter(
                StringReading.string_id == string_id,
                StringReading.recorded_at >= start,
                StringReading.irradiance.between(
                    irradiance - irradiance_band, irradiance + irradiance_band
                ),
                StringReading.temperature.between(
                    temperature - temp_band, temperature + temp_band
                ),
            )
            .all()
        )
        powers = sorted(r[0] for r in rows if r[0] is not None)
        if len(powers) < min_samples:
            return None
        mid = len(powers) // 2
        return float(powers[mid])