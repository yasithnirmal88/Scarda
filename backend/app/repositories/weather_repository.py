from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.weather_reading import WeatherReading


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
