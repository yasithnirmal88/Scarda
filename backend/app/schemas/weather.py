from datetime import datetime

from pydantic import BaseModel


class WeatherCreate(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    irradiance: float | None = None
    wind_speed: float | None = None
    wind_direction: str | None = None
    precipitation: float | None = None


class WeatherResponse(WeatherCreate):
    id: int
    recorded_at: datetime

    model_config = {"from_attributes": True}
