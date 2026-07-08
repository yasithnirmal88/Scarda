from datetime import datetime

from pydantic import BaseModel


class StringReadingCreate(BaseModel):
    string_id: int
    voltage: float | None = None
    current: float | None = None
    power: float | None = None
    temperature: float | None = None
    irradiance: float | None = None


class StringReadingResponse(StringReadingCreate):
    id: int
    recorded_at: datetime

    model_config = {"from_attributes": True}
