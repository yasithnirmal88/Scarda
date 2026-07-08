from datetime import datetime

from pydantic import BaseModel


class StringBase(BaseModel):
    inverter_id: int
    name: str
    panel_count: int = 0
    status: str = "active"


class StringCreate(StringBase):
    pass


class StringUpdate(BaseModel):
    name: str | None = None
    panel_count: int | None = None
    status: str | None = None


class StringResponse(StringBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
