from datetime import date, datetime, timedelta, timezone

from pydantic import BaseModel, field_validator

from .models import AttendanceStatus


class EvaluationGradeCreate(BaseModel):
    name: str
    grade: int


type EvaluationGradeUpdate = EvaluationGradeCreate


class StudentEvaluationCreate(BaseModel):
    attendance_status: AttendanceStatus
    notes: str = ""
    evaluations: list[EvaluationGradeCreate] | None = []


type StudentEvaluationUpdate = StudentEvaluationCreate


class BulkEvaluationCreate(BaseModel):
    class_id: int
    date: str  # YYYY-MM-DD
    unit_item_id: int
    records: dict[int, StudentEvaluationCreate]  # student_id -> evaluation data

    @field_validator("date")
    def validate_date_not_future(cls, v):
        eval_date = date.fromisoformat(v)

        gmt2 = timezone(timedelta(hours=2))
        today_gmt2 = datetime.now(gmt2).date()

        if eval_date > today_gmt2:
            raise ValueError("Date cannot be in the future")
        return v


class BulkEvaluationUpdate(BaseModel):
    class_id: int
    date: str
    unit_item_id: int
    records: dict[int, StudentEvaluationUpdate]

    @field_validator("date")
    def validate_date_not_future(cls, v):
        eval_date = date.fromisoformat(v)

        gmt2 = timezone(timedelta(hours=2))
        today_gmt2 = datetime.now(gmt2).date()

        if eval_date > today_gmt2:
            raise ValueError("Date cannot be in the future")
        return v


class ListEvaluationsResponseItem(BaseModel):
    id: int
    student_id: int
    class_id: int
    branch_id: int
    unit_item_id: int
    unit_item_title: str
    unit_item_content: str
    date: str
    attendance_status: str
    evaluation_grades: list[dict]
    notes: str | None
    created_at: str
