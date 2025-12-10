from typing import Dict, List

from app.db.base import Base
from app.modules.evaluations.models import AttendanceStatus
from app.modules.reports.models.base import BaseReport
from pydantic import BaseModel, field_serializer
from sqlalchemy import (
    JSON,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship


class StudentReport(BaseReport):
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )

    @declared_attr
    def student(cls):
        return relationship("Student")


class StudentReportData(BaseModel):
    branch_id: int
    branch_name: str
    class_id: int
    class_name: str
    student_id: int
    student_name: str
    date: str


class StudentAttendanceReportData(StudentReportData):
    type: str = "attendance"
    status: AttendanceStatus

    @field_serializer("status")
    def serialize_status(self, status: AttendanceStatus):
        arabic_mapping = {
            AttendanceStatus.PRESENT: "حاضر",
            AttendanceStatus.ABSENT: "غائب",
            AttendanceStatus.LATE: "متأخر",
            AttendanceStatus.EXCUSED: "معتذر",
        }
        return arabic_mapping.get(status, str(status))


class StudentAttendanceReport(StudentReport, Base):
    __tablename__ = "attendance_reports"
    report_data: Mapped[List[StudentAttendanceReportData]] = mapped_column(
        JSON, nullable=False
    )


class StudentEvaluationReportData(StudentReportData):
    type: str = "evaluation"
    evaluation_grades: List[Dict]


class StudentEvaluationReport(StudentReport, Base):
    __tablename__ = "evaluation_reports"
    report_data: Mapped[StudentEvaluationReportData] = mapped_column(
        JSON, nullable=False
    )
