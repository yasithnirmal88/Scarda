from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

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