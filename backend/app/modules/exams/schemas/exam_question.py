from pydantic import BaseModel
from typing import Optional


class ExamQuestionBase(BaseModel):
    question_id: int
    marks: int
    order: int


class ExamQuestionCreate(ExamQuestionBase):
    pass


class AddQuestionToExam(BaseModel):
    questions: list[ExamQuestionCreate]


class ExamQuestionUpdate(BaseModel):
    marks: Optional[int] = None
    order: Optional[int] = None


class ExamQuestionRead(ExamQuestionBase):
    id: int
    exam_id: int
    branch_id: int

    class Config:
        from_attributes = True
