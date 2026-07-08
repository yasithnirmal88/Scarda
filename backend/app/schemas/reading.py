from datetime import datetime

from pydantic import BaseModel


class StringReadingCreate(BaseModel):
    string_id: int
    voltage: float | None = None
    current: float | None = None
    power: float | None = None
    temperature: float | None = None
    irradiance: float | None = None


class StringReadingResponse(BaseModel):
    id: int
    string_id: int
    recorded_at: datetime
    voltage: float | None
    current: float | None
    power: float | None
    temperature: float | None
    irradiance: float | None

    model_config = {"from_attributes": True}
