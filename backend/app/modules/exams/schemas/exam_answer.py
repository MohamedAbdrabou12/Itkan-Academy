from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExamAnswerBase(BaseModel):
    attempt_id: int
    question_id: int
    chosen_option: Optional[str] = None
    is_correct: Optional[bool] = None


class ExamAnswerCreate(ExamAnswerBase):
    pass


class ExamAnswerUpdate(BaseModel):
    chosen_option: Optional[str] = None
    is_correct: Optional[bool] = None


class ExamAnswerRead(ExamAnswerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
