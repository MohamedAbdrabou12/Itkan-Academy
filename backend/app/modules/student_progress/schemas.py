from datetime import date, datetime
from enum import Enum

from app.modules.curriculums.models.unit_item import UnitItemType
from app.modules.evaluations.models import AttendanceStatus
from app.modules.exams.models.exam_attempt import ExamAttemptStatus
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
    notes: str | None
    date: date


class StudentProgressExamInfo(BaseModel):
    id: int
    title: str
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    total_marks: int


class StudentProgressStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"


class StudentProgressExamAttemptInfo(BaseModel):
    id: int
    exam_info: StudentProgressExamInfo
    status: ExamAttemptStatus
    start_time: datetime
    end_time: datetime
    score: float


class StudentProgressEntry(BaseModel):
    id: int
    student_info: StudentProgressStudentInfo
    status: StudentProgressStatus
    unit_item_info: StudentProgressUnitItemInfo
    evaluation_info: StudentProgressEvaluationInfo | None = None
    exam_attempt_info: StudentProgressExamAttemptInfo | None = None
    created_at: datetime


class StudentProgressClassGroup(BaseModel):
    class_id: int
    class_name: str
    subject_name: str
    curriculum_name: str
    unit_items_info: list[StudentProgressUnitItemInfo]
    items: list[StudentProgressEntry]


class StudentProgressStudentGroupBase(BaseModel):
    student_id: int
    student_name: str


class StudentProgressStudentGroupResponse(StudentProgressStudentGroupBase):
    groups: list[StudentProgressClassGroup]


class StudentProgressStudentGroupInternal(StudentProgressStudentGroupBase):
    groups: dict[int, StudentProgressClassGroup]
