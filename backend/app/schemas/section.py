from datetime import datetime

from pydantic import BaseModel


class SectionCreate(BaseModel):
    name: str
    description: str | None = None


class SectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class SectionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
