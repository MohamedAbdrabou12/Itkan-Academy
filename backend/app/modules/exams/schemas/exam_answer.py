from pydantic import BaseModel, model_validator
from typing import Optional, List

from app.modules.question_bank.models import QuestionType


class ExamAnswerBase(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    selected_option: Optional[str] = None


class ExamAnswerCreate(ExamAnswerBase):
    attempt_id: int


class ExamAnswerUpdate(BaseModel):
    answer_text: Optional[str] = None
    selected_option: Optional[str] = None
    marks_obtained: Optional[float] = None


class ExamAnswerRead(ExamAnswerBase):
    id: int
    attempt_id: int

    class Config:
        from_attributes = True


class ExamAnswerBulkItem(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    selected_option: Optional[str] = None


class ExamAnswerBulkItemSubmit(ExamAnswerBase):
    marks_obtained: Optional[int] = None


class ExamAnswerBulkCreate(BaseModel):
    answers: List[ExamAnswerBulkItem]


class ExamAnswerResponse(BaseModel):
    id: int
    marks: int
    order: int
    title: str
    options: dict
    type: QuestionType
    answer_text: Optional[str] = None
    selected_option: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def flatten_from_orm(cls, data):
        # When creating from an ORM model instance
        if hasattr(data, "question"):
            question_details = data.question
            return {
                "id": question_details.question.id,
                "marks": question_details.marks,
                "order": question_details.order,
                "title": question_details.question.title,
                "options": question_details.question.options,
                "type": question_details.question.type,
                "answer_text": data.answer_text,
                "selected_option": data.selected_option,
            }
        return data
