from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class DailyEvaluationBase(BaseModel):
    student_id: int
    class_id: int
    date: date
    memorization_percent: Optional[float] = None
    behavior_score: Optional[int] = None
    notes: Optional[str] = None
    recorded_by: Optional[int] = None


class DailyEvaluationCreate(DailyEvaluationBase):
    pass


class DailyEvaluationUpdate(BaseModel):
    memorization_percent: Optional[float] = None
    behavior_score: Optional[int] = None
    notes: Optional[str] = None
    recorded_by: Optional[int] = None


class DailyEvaluationRead(DailyEvaluationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
