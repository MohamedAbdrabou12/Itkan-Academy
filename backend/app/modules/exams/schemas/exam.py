from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from typing import Optional, List

from app.modules.exams.models.exam import ExamStatus
from app.modules.question_bank.models import (
    QuestionDifficulty,
    QuestionType,
)


class ExamQuestionWithDetails(BaseModel):
    id: int
    marks: int
    order: int
    title: str
    difficulty: QuestionDifficulty
    options: dict
    type: QuestionType

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def flatten_from_orm(cls, data):
        # When creating from an ORM model instance
        if hasattr(data, "question"):
            question_details = data.question
            return {
                "id": data.id,
                "marks": data.marks,
                "order": data.order,
                "title": question_details.title,
                "difficulty": question_details.difficulty,
                "options": question_details.options,
                "type": question_details.type,
            }
        return data


class ExamBase(BaseModel):
    title: str
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    class_id: int


class ExamCreate(ExamBase):
    @field_validator("end_time")
    @classmethod
    def end_time_must_be_after_start_time(cls, v, values):
        if "start_time" in values.data and v <= values.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ExamUpdate(BaseModel):
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    class_id: Optional[int] = None

    @field_validator("end_time")
    @classmethod
    def end_time_must_be_after_start_time(cls, v, values):
        data = values.data
        start_time = data.get("start_time")

        if "start_time" in data and v and start_time and v <= start_time:
            raise ValueError("end_time must be after start_time")
        return v


class ExamRead(ExamBase):
    id: int
    total_marks: int
    status: ExamStatus
    branch_id: int
    created_by: int
    questions: Optional[List[ExamQuestionWithDetails]] = []

    class Config:
        from_attributes = True
