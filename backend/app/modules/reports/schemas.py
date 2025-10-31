from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class ReportJobBase(BaseModel):
    type: str
    params: Optional[Dict] = None
    status: Optional[str] = "queued"
    result_url: Optional[str] = None
    created_by: Optional[int] = None


class ReportJobCreate(ReportJobBase):
    pass


class ReportJobUpdate(BaseModel):
    status: Optional[str] = None
    result_url: Optional[str] = None


class ReportJobRead(ReportJobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
