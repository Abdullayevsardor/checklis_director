from datetime import datetime
from pydantic import BaseModel


class ShiftCheckReportOut(BaseModel):
    id: int
    branch_id: int
    # checklist_id: int
    status: str
    started_at: datetime | None
    submitted_at: datetime | None

    class Config:
        from_attributes = True


 