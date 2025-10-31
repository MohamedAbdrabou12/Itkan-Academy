from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExamAttemptBase(BaseModel):
    exam_id: int
    student_id: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    score: Optional[float] = None
    status: Optional[str] = "in-progress"


class ExamAttemptCreate(ExamAttemptBase):
    pass


class ExamAttemptUpdate(BaseModel):
    finished_at: Optional[datetime] = None
    score: Optional[float] = None
    status: Optional[str] = None


class ExamAttemptRead(ExamAttemptBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
