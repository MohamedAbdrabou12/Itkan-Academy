from datetime import date, datetime
from typing import Dict, Optional

from pydantic import BaseModel


class StudentBase(BaseModel):
    user_id: int
    parent_user_id: Optional[int] = None
    branch_id: int
    class_id: Optional[int] = None
    admission_date: Optional[date] = None
    status: Optional[str] = "active"
    curriculum_progress: Optional[Dict] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    parent_user_id: Optional[int] = None
    branch_id: Optional[int] = None
    class_id: Optional[int] = None
    admission_date: Optional[date] = None
    status: Optional[str] = None
    curriculum_progress: Optional[Dict] = None


class StudentRead(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
