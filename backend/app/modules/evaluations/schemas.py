from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from .models import AttendanceStatus


class EvaluationGradeCreate(BaseModel):
    name: str
    grade: int


type EvaluationGradeUpdate = EvaluationGradeCreate


class StudentEvaluationCreate(BaseModel):
    attendance_status: AttendanceStatus
    notes: str = ""
    evaluations: Optional[List[EvaluationGradeCreate]] = []


class StudentEvaluationUpdate(BaseModel):
    attendance_status: Optional[AttendanceStatus]
    notes: Optional[str]
    evaluations: Optional[List[EvaluationGradeUpdate]]


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


class BulkEvaluationUpdate(BaseModel):
    class_id: int
    date: str
    records: Dict[int, StudentEvaluationUpdate]

    @field_validator("date")
    def validate_date_not_future(cls, v):
        """Ensure date is not in the future"""
        eval_date = date.fromisoformat(v)
        if eval_date > date.today():
            raise ValueError("Date cannot be in the future")
        return v


class ListEvaluationsResponseItem(BaseModel):
    id: int
    student_id: int
    class_id: int
    date: str
    attendance_status: str
    evaluation_grades: List[Dict]
    notes: Optional[str]
    created_at: str
