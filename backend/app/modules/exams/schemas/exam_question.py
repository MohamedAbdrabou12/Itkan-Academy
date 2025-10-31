from typing import Optional
from pydantic import BaseModel


class ExamQuestionBase(BaseModel):
    exam_id: int
    question_id: int
    question_order: Optional[int] = None


class ExamQuestionCreate(ExamQuestionBase):
    pass


class ExamQuestionUpdate(BaseModel):
    question_order: Optional[int] = None


class ExamQuestionRead(ExamQuestionBase):
    class Config:
        from_attributes = True
