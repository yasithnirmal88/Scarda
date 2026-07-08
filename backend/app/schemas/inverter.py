from datetime import datetime

from pydantic import BaseModel


class InverterCreate(BaseModel):
    section_id: int
    name: str
    model_number: str | None = None
    status: str = "offline"


class InverterUpdate(BaseModel):
    name: str | None = None
    model_number: str | None = None
    status: str | None = None


class InverterResponse(BaseModel):
    id: int
    section_id: int
    name: str
    model_number: str | None
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
