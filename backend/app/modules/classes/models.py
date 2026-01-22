from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from app.db.base import Base
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.curriculums.models.curriculum import Curriculum
    from app.modules.curriculums.models.subject import Subject

    from backend.backend.app.modules.branches.models import Branch
    from backend.backend.app.modules.evaluations.models import Evaluation
    from backend.backend.app.modules.exams.models.exam import Exam
    from backend.backend.app.modules.students.models import Student, StudentClass
    from backend.backend.app.modules.teachers.models import Teacher, TeacherClass


class ClassStatus(Enum):
    active = "active"
    deactive = "deactive"


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
    )
    curriculum_id: Mapped[int] = mapped_column(ForeignKey("curriculums.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    schedule: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[ClassStatus] = mapped_column(
        String(10), default=ClassStatus.active.value, nullable=False
    )
    evaluation_config: Mapped[list[str]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student_links: Mapped[list[StudentClass]] = relationship(
        "StudentClass",
        back_populates="class_",
        cascade="all, delete-orphan",
    )
    students: Mapped[list[Student]] = relationship(
        "Student",
        secondary="student_classes",
        back_populates="classes",
        overlaps="class_,student_links",
    )
    branch: Mapped[Branch] = relationship("Branch", back_populates="classes")
    curriculum: Mapped[Curriculum] = relationship(
        "Curriculum", back_populates="class_links", lazy="selectin"
    )
    subject: Mapped[Subject] = relationship(
        "Subject", back_populates="class_links", lazy="selectin"
    )
    daily_evaluations: Mapped[list[Evaluation]] = relationship(
        "Evaluation", back_populates="class_"
    )
    teachers: Mapped[list[Teacher]] = relationship(
        "Teacher",
        secondary="teacher_classes",
        back_populates="classes",
    )
    teacher_links: Mapped[list[TeacherClass]] = relationship(
        "TeacherClass",
        back_populates="class_",
        cascade="all, delete-orphan",
    )
    exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="class_")
