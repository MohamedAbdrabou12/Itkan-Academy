from typing import Dict, List

from pydantic import BaseModel
from app.modules.reports.models.base import BaseReport
from sqlalchemy import (
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from app.db.base import Base
from app.modules.evaluations.models import AttendanceStatus


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
