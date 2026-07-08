from datetime import datetime

from pydantic import BaseModel


class SectionBase(BaseModel):
    name: str
    description: str | None = None


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class SectionResponse(SectionBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
