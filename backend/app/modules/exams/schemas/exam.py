from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExamBase(BaseModel):
    title: str
    branch_id: Optional[int] = None
    class_id: Optional[int] = None
    created_by: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_published: Optional[bool] = False


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    title: Optional[str] = None
    branch_id: Optional[int] = None
    class_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_published: Optional[bool] = None


class ExamRead(ExamBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
