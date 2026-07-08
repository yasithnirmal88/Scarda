from datetime import datetime

from pydantic import BaseModel


class ReportRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    section_id: int | None = None
    inverter_id: int | None = None


class ReportResponse(BaseModel):
    message: str
    report_type: str
    generated_at: datetime
