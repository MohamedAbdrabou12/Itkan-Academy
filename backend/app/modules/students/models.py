from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from app.db.base import Base
from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.attendance.models import Attendance
    from app.modules.classes.models import Class
    from app.modules.evaluations.models import DailyEvaluation
    from app.modules.financial.models.invoice import Invoice
    from app.modules.users.models import User


class StudentClass(Base):
    __tablename__ = "student_classes"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"), primary_key=True
    )
    enrollment_date: Mapped[Optional[date]] = mapped_column(Date, default=date.today)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    progress_percent: Mapped[Optional[float]] = mapped_column(default=0.0)
    final_grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    last_attendance: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    student: Mapped["Student"] = relationship(
        "Student", back_populates="class_links", lazy="selectin"
    )
    class_: Mapped["Class"] = relationship(
        "Class", back_populates="student_links", lazy="selectin"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    admission_date: Mapped[Optional[date]] = mapped_column(Date)
    curriculum_progress: Mapped[Optional[Dict]] = mapped_column(
        JSON, default=None, nullable=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student", lazy="joined")

    class_links: Mapped[List["StudentClass"]] = relationship(
        "StudentClass",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    classes: Mapped[List["Class"]] = relationship(
        "Class",
        secondary="student_classes",
        back_populates="students",
        lazy="selectin",
    )

    attendance_records: Mapped[List["Attendance"]] = relationship(
        "Attendance", back_populates="student", lazy="selectin"
    )
    evaluations: Mapped[List["DailyEvaluation"]] = relationship(
        "DailyEvaluation", back_populates="student", lazy="selectin"
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", back_populates="student", lazy="selectin"
    )

    @property
    def branch_ids(self) -> List[int]:
        if self.user and self.user.branches:
            return [b.id for b in self.user.branches]
        return []

    def __repr__(self):
        name = getattr(self.user, "full_name", None)
        return f"<Student(id={self.id}, user={name})>"
