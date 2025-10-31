from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class AttendanceBase(BaseModel):
    student_id: int
    class_id: int
    date: date
    status: str
    recorded_by: Optional[int] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    recorded_by: Optional[int] = None


class AttendanceRead(AttendanceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
