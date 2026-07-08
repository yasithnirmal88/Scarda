from datetime import datetime

from pydantic import BaseModel


class StringCreate(BaseModel):
    inverter_id: int
    name: str
    panel_count: int = 0
    status: str = "active"


class StringUpdate(BaseModel):
    name: str | None = None
    panel_count: int | None = None
    status: str | None = None


class StringResponse(BaseModel):
    id: int
    inverter_id: int
    name: str
    panel_count: int
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
