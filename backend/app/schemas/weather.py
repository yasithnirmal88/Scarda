from datetime import datetime

from pydantic import BaseModel


class WeatherCreate(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    irradiance: float | None = None
    wind_speed: float | None = None
    wind_direction: str | None = None
    precipitation: float | None = None


class WeatherResponse(BaseModel):
    id: int
    recorded_at: datetime
    temperature: float | None
    humidity: float | None
    irradiance: float | None
    wind_speed: float | None
    wind_direction: str | None
    precipitation: float | None

    model_config = {"from_attributes": True}
