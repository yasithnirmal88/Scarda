from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    inverter_id: int | None = None
    string_id: int | None = None
    type: str
    severity: str
    message: str
    status: str = "active"


class AlertUpdate(BaseModel):
    status: str | None = None
    resolved_at: datetime | None = None


class AlertResponse(BaseModel):
    id: int
    inverter_id: int | None
    string_id: int | None
    type: str
    severity: str
    message: str
    status: str
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}
