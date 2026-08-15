from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any

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

    def bulk_create(self, readings: list[StringReading]) -> None:
        """Persist many readings in one transaction.

        Used by the historical backfill path that ingests a whole batch from the
        provider while preserving each reading's original measurement timestamp.
        On PostgreSQL/TimescaleDB this is idempotent: rows that collide on the
        (string_id, recorded_at) unique constraint are skipped via ON CONFLICT,
        so re-running a backfill does not duplicate history.
        """
        if not readings:
            return
        try:
            dialect = self.db.bind.dialect.name if self.db.bind else "sqlite"
        except Exception:
            dialect = "sqlite"

        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            def _row_dict(r: StringReading) -> dict[str, Any]:
                return {
                    "string_id": r.string_id,
                    "recorded_at": r.recorded_at,
                    "voltage": r.voltage,
                    "current": r.current,
                    "power": r.power,
                    "temperature": r.temperature,
                    "irradiance": r.irradiance,
                }

            # Dedupe by (string_id, recorded_at) within the batch — Postgres
            # rejects "ON CONFLICT DO UPDATE ... affect row a second time" when
            # the same key appears more than once in one statement. Keep the
            # last value per key (later reading wins).
            seen: dict[tuple[int, datetime], dict[str, Any]] = {}
            for r in readings:
                seen[(r.string_id, r.recorded_at)] = _row_dict(r)
            deduped = list(seen.values())

            # Chunk so we stay under Postgres' 65535 bind-parameter limit
            # (7 cols × ~5000 rows ≈ 35k params, well under the cap) and keep
            # each statement's memory bounded.
            BATCH = 5000
            total = 0
            try:
                for i in range(0, len(deduped), BATCH):
                    chunk = deduped[i : i + BATCH]
                    stmt = pg_insert(StringReading).values(chunk)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["string_id", "recorded_at"],
                        set_={
                            "voltage": stmt.excluded.voltage,
                            "current": stmt.excluded.current,
                            "power": stmt.excluded.power,
                            "temperature": stmt.excluded.temperature,
                            "irradiance": stmt.excluded.irradiance,
                        },
                    )
                    self.db.execute(stmt)
                    total += len(chunk)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return total

        try:
            self.db.add_all(readings)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

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

        For the richer robust-statistics result (median + MAD + sample count +
        time-of-day window), prefer ``similarity_for_conditions``.
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

    def similarity_for_conditions(
        self,
        string_id: int,
        irradiance: float,
        temperature: float,
        *,
        reference_at: datetime | None = None,
        irradiance_band: float = 100.0,
        temp_band: float = 3.0,
        time_of_day_band_hours: float = 2.0,
        lookback_days: int = 14,
        min_samples: int = 5,
    ) -> dict | None:
        """Robust historical similarity lookup for one string.

        Finds historical ``StringReading`` rows for the same string, within a
        configurable lookback window, with similar irradiance (+/-
        ``irradiance_band`` W/m²), similar temperature (+/- ``temp_band`` °C),
        and — to avoid comparing an 08:00 reading with a 13:00 reading — within
        ``time_of_day_band_hours`` of the reference reading's hour-of-day
        (unless ``reference_at`` is None, in which case the time-of-day filter
        is skipped).

        Returns a dict with the robust expected-power statistics:

            {
              "sample_count": int,
              "median_power": float,
              "mad": float,            # median absolute deviation
              "iqr": float,            # interquartile range (dispersion)
              "min_power": float,
              "max_power": float,
              "powers": [float, ...],  # matched samples (for inspection)
            }

        or ``None`` when fewer than ``min_samples`` matches exist (so the caller
        can fall back to the physics model). This is the Tier-2 historical
        baseline's source of truth; MAD is used instead of standard deviation
        because it is robust to the occasional bad/outlier sample.
        """
        start = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        stmt = self.db.query(StringReading).filter(
            StringReading.string_id == string_id,
            StringReading.recorded_at >= start,
            StringReading.irradiance.between(
                irradiance - irradiance_band, irradiance + irradiance_band
            ),
            StringReading.temperature.between(
                temperature - temp_band, temperature + temp_band
            ),
        )

        if reference_at is not None and time_of_day_band_hours > 0:
            ref_hour = reference_at.astimezone(timezone.utc).hour
            # Use EXTRACT(hour ...) so the comparison is time-of-day only; this
            # keeps an 08:00 reading from matching a 13:00 reading even when
            # irradiance/temperature happen to coincide.
            hour_expr = sa_func.extract("hour", StringReading.recorded_at)
            lo = (ref_hour - time_of_day_band_hours) % 24
            hi = (ref_hour + time_of_day_band_hours) % 24
            if lo <= hi:
                stmt = stmt.filter(hour_expr.between(lo, hi))
            else:
                # window wraps midnight
                stmt = stmt.filter((hour_expr >= lo) | (hour_expr <= hi))

        rows = stmt.all()
        powers = sorted(r.power for r in rows if r.power is not None)
        if len(powers) < min_samples:
            return None

        median = _median(powers)
        deviations = sorted(abs(p - median) for p in powers)
        mad = _median(deviations)
        q1 = _percentile(powers, 25)
        q3 = _percentile(powers, 75)
        return {
            "sample_count": len(powers),
            "median_power": float(median),
            "mad": float(mad),
            "iqr": float(q3 - q1),
            "min_power": float(powers[0]),
            "max_power": float(powers[-1]),
            "powers": [float(p) for p in powers],
        }


def _median(sorted_values: list[float]) -> float:
    n = len(sorted_values)
    mid = n // 2
    if n % 2 == 1:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0


def _percentile(sorted_values: list[float], pct: float) -> float:
    """Linear-interpolation percentile on an already-sorted list."""
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = rank - lo
    return float(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac)