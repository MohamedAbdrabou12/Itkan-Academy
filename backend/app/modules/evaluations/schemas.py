from datetime import date
from .models import AttendanceStatus
from typing import List, Dict

from pydantic import BaseModel, field_validator


class EvaluationGradeCreate(BaseModel):
    name: str
    grade: int


class StudentEvaluationCreate(BaseModel):
    status: AttendanceStatus
    notes: str = ""
    evaluations: List[EvaluationGradeCreate] = []


class BulkEvaluationCreate(BaseModel):
    class_id: int
    date: str  # YYYY-MM-DD
    records: Dict[int, StudentEvaluationCreate]  # student_id -> evaluation data

    @field_validator("date")
    def validate_date_not_future(cls, v):
        """Ensure date is not in the future"""
        eval_date = date.fromisoformat(v)
        if eval_date > date.today():
            raise ValueError("Date cannot be in the future")
        return v
