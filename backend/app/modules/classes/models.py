from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Dict, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.branches.models import Branch  # noqa: F401
    from app.modules.students.models import Student, StudentClass  # noqa: F401
    from app.modules.evaluations.models import Evaluation  # noqa: F401
    from app.modules.teachers.models import Teacher, TeacherClass  # noqa: F401
    from app.modules.exams.models import Exam  # noqa: F401


class ClassStatus(Enum):
    active = "active"
    deactive = "deactive"


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    schedule: Mapped[Dict] = mapped_column(JSONB)
    status: Mapped[ClassStatus] = mapped_column(
        String(10), default=ClassStatus.active.value, nullable=False
    )
    evaluation_config: Mapped[List[str]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student_links: Mapped[List["StudentClass"]] = relationship(
        "StudentClass",
        back_populates="class_",
        cascade="all, delete-orphan",
    )
    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary="student_classes",
        back_populates="classes",
        overlaps="class_,student_links",
    )
    branch: Mapped["Branch"] = relationship("Branch", back_populates="classes")
    daily_evaluations: Mapped[List["Evaluation"]] = relationship(
        "Evaluation", back_populates="class_"
    )
    teachers: Mapped[List["Teacher"]] = relationship(
        "Teacher",
        secondary="teacher_classes",
        back_populates="classes",
    )
    teacher_links: Mapped[List["TeacherClass"]] = relationship(
        "TeacherClass",
        back_populates="class_",
        cascade="all, delete-orphan",
    )
    exams: Mapped[List["Exam"]] = relationship("Exam", back_populates="class_")
