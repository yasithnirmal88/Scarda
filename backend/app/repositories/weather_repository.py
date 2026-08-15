from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.models.telemetry.weather_reading import WeatherReading


class WeatherRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, reading: WeatherReading) -> WeatherReading:
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def bulk_create(self, readings: list[WeatherReading]) -> None:
        """Persist many weather readings in one transaction.

        Idempotent on PostgreSQL/TimescaleDB: rows that collide on the
        ``recorded_at`` unique constraint are updated (ON CONFLICT DO UPDATE),
        so re-running a weather backfill does not duplicate samples.
        """
        if not readings:
            return
        try:
            dialect = self.db.bind.dialect.name if self.db.bind else "sqlite"
        except Exception:
            dialect = "sqlite"

        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            def _row_dict(r: WeatherReading) -> dict[str, Any]:
                return {
                    "recorded_at": r.recorded_at,
                    "temperature": r.temperature,
                    "humidity": r.humidity,
                    "irradiance": r.irradiance,
                    "wind_speed": r.wind_speed,
                    "wind_direction": r.wind_direction,
                    "precipitation": r.precipitation,
                }

            # Dedupe by recorded_at within the batch (last value wins) to avoid
            # Postgres' "ON CONFLICT DO UPDATE ... affect row a second time".
            seen: dict[datetime, dict[str, Any]] = {}
            for r in readings:
                seen[r.recorded_at] = _row_dict(r)
            deduped = list(seen.values())

            BATCH = 5000
            total = 0
            try:
                for i in range(0, len(deduped), BATCH):
                    chunk = deduped[i : i + BATCH]
                    stmt = pg_insert(WeatherReading).values(chunk)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["recorded_at"],
                        set_={
                            "temperature": stmt.excluded.temperature,
                            "humidity": stmt.excluded.humidity,
                            "irradiance": stmt.excluded.irradiance,
                            "wind_speed": stmt.excluded.wind_speed,
                            "wind_direction": stmt.excluded.wind_direction,
                            "precipitation": stmt.excluded.precipitation,
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

    def find_all(self) -> Sequence[WeatherReading]:
        return self.db.query(WeatherReading).all()

    def find_latest(self) -> WeatherReading | None:
        return (
            self.db.query(WeatherReading)
            .order_by(WeatherReading.recorded_at.desc())
            .first()
        )

    def find_between(self, start: datetime, end: datetime) -> Sequence[WeatherReading]:
        return (
            self.db.query(WeatherReading)
            .filter(WeatherReading.recorded_at >= start, WeatherReading.recorded_at < end)
            .all()
        )

    def average_temperature_between(self, start: datetime, end: datetime) -> float | None:
        result = (
            self.db.query(sa_func.avg(WeatherReading.temperature))
            .filter(WeatherReading.recorded_at >= start, WeatherReading.recorded_at < end)
            .scalar()
        )
        return float(result) if result is not None else None