from datetime import datetime

from pydantic import BaseModel


class MaintenanceCreate(BaseModel):
    inverter_id: int | None = None
    string_id: int | None = None
    user_id: int
    title: str
    description: str | None = None
    scheduled_date: datetime | None = None
    status: str = "scheduled"


class MaintenanceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    scheduled_date: datetime | None = None
    completed_date: datetime | None = None
    status: str | None = None


class MaintenanceResponse(BaseModel):
    id: int
    inverter_id: int | None
    string_id: int | None
    user_id: int
    title: str
    description: str | None
    scheduled_date: datetime | None
    completed_date: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
