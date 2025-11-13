from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional

from app.modules.exams.models.exam_attempt import ExamAttemptStatus
from app.modules.question_bank.models import QuestionType


class ExamAttemptBase(BaseModel):
    exam_id: int


class ExamAttemptCreate(ExamAttemptBase):
    pass


class ExamAttemptUpdate(BaseModel):
    status: Optional[ExamAttemptStatus] = None
    score: Optional[float] = None
    end_time: Optional[datetime] = None


class ExamQuestionWithDetails(BaseModel):
    id: int
    marks: int
    title: str
    options: dict
    selected_option: Optional[str] = None
    answer_text: Optional[str] = None
    marks_obtained: Optional[int] = None
    type: QuestionType

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def flatten_from_orm(cls, data):
        if hasattr(data, "question"):
            question_details = data.question
            return {
                "id": data.id,
                "marks": data.question.marks,
                "title": question_details.question.title,
                "options": question_details.question.options,
                "type": question_details.question.type,
                "selected_option": data.selected_option,
                "answer_text": data.answer_text,
                "marks_obtained": data.marks_obtained,
            }
        return data


class ExamAttemptRead(ExamAttemptBase):
    student_id: int
    id: int
    status: ExamAttemptStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    score: Optional[float] = None

    class Config:
        from_attributes = True


class ExamAttemptResponse(ExamAttemptRead):
    answers: list[ExamQuestionWithDetails]


class ExamQuestionAnswers(BaseModel):
    id: int
    marks: int
    title: str
    options: dict
    selected_option: Optional[str] = None
    answer_text: Optional[str] = None
    marks_obtained: int
    type: QuestionType

    # if the question type is mcq, the question should has a selected_option
    @model_validator(mode="after")
    @classmethod
    def validate_question_type(cls, data):
        if (
            data.type == QuestionType.MCQ or data.type == QuestionType.TRUE_FALSE
        ) and data.selected_option is None:
            raise ValueError("For MCQ questions, 'selected_option' must be provided.")
        if (
            data.type == QuestionType.ESSAY or data.type == QuestionType.SHORT_ANSWER
        ) and data.answer_text is None:
            raise ValueError("For ESSAY questions, 'answer_text' must be provided.")

        return data

    class Config:
        from_attributes = True


class ExamAttemptTeacherResponse(ExamAttemptRead):
    answers: list[ExamQuestionAnswers]
