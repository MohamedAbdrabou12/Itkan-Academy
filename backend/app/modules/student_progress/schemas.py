from datetime import date, datetime

from app.modules.curriculums.models.unit_item import UnitItemType
from app.modules.evaluations.models import AttendanceStatus
from app.modules.exams.models.exam_attempt import ExamAttemptStatus
from app.modules.student_progress.models import StudentProgressStatus
from pydantic import BaseModel


class StudentProgressStudentInfo(BaseModel):
    id: int
    name: str


class StudentProgressUnitInfo(BaseModel):
    id: int
    title: str


class StudentProgressUnitItemInfo(BaseModel):
    id: int
    title: str
    type: UnitItemType
    unit_info: StudentProgressUnitInfo


class StudentProgressEvaluationInfo(BaseModel):
    id: int
    attendance_status: AttendanceStatus
    evaluation_grades: list[dict]
    date: date


class StudentProgressExamInfo(BaseModel):
    id: int
    title: str
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    total_marks: int


class StudentProgressExamAttemptInfo(BaseModel):
    id: int
    exam_info: StudentProgressExamInfo
    status: ExamAttemptStatus
    start_time: datetime
    end_time: datetime
    score: int


class StudentProgressBySubjectEntry(BaseModel):
    id: int
    student_info: StudentProgressStudentInfo
    status: StudentProgressStatus
    unit_item_info: StudentProgressUnitItemInfo
    evaluation_info: StudentProgressEvaluationInfo | None = None
    exam_attempt_info: StudentProgressExamAttemptInfo | None = None
    created_at: datetime


class StudentProgressBySubjectList(BaseModel):
    subject_id: int
    subject_name: str
    unit_items_info: list[StudentProgressUnitItemInfo]
    items: list[StudentProgressBySubjectEntry]


class StudentProgressByStudentList(BaseModel):
    student_id: int
    student_name: str
    groups: list[StudentProgressBySubjectList]
