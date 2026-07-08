from sqlalchemy import Column, DateTime, Float, Integer
from sqlalchemy.sql import func

from app.database.base import Base


class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id = Column(Integer, primary_key=True, index=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    irradiance = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(String(10), nullable=True)
    precipitation = Column(Float, nullable=True)
