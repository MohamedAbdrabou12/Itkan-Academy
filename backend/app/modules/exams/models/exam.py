from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.classes.models import Class
    from app.modules.users.models import User
    from app.modules.branches.models import Branch
    from .exam_question import ExamQuestion
    from .exam_attempt import ExamAttempt


class ExamStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_marks: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ExamStatus] = mapped_column(String(20), default=ExamStatus.DRAFT)

    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    class_: Mapped["Class"] = relationship(lazy="selectin")
    branch: Mapped["Branch"] = relationship(lazy="selectin")
    creator: Mapped["User"] = relationship(lazy="selectin")
    questions: Mapped[List["ExamQuestion"]] = relationship(
        "ExamQuestion",
        back_populates="exam",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attempts: Mapped[List["ExamAttempt"]] = relationship(
        "ExamAttempt", back_populates="exam", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("title", "branch_id", name="uq_exam_title_branch"),
    )
