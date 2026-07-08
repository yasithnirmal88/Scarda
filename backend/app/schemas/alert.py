from datetime import datetime

from pydantic import BaseModel


class AlertBase(BaseModel):
    inverter_id: int | None = None
    string_id: int | None = None
    type: str
    severity: str
    message: str
    status: str = "active"


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: str | None = None
    resolved_at: datetime | None = None


class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}
