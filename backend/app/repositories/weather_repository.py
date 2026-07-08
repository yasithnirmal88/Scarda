from sqlalchemy.orm import Session

from app.models.weather import WeatherReading
from app.repositories.base import BaseRepository


class WeatherRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all(self) -> list[WeatherReading]:
        return self.db.query(WeatherReading).all()

    def get_latest(self) -> WeatherReading | None:
        return self.db.query(WeatherReading).order_by(WeatherReading.recorded_at.desc()).first()
