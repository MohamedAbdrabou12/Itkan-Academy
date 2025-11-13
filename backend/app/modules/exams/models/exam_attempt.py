import enum
from datetime import datetime
from typing import TYPE_CHECKING, List
from app.db.base import Base
from sqlalchemy import DateTime, Float, ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.users.models import User
    from .exam import Exam
    from .exam_answer import ExamAnswer


class ExamAttemptStatus(str, enum.Enum):
    STARTED = "started"
    SUBMITTED = "submitted"
    GRADED = "graded"


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"))

    status: Mapped[ExamAttemptStatus] = mapped_column(
        Enum(ExamAttemptStatus), default=ExamAttemptStatus.STARTED
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    student: Mapped["User"] = relationship(back_populates="exam_attempts")
    exam: Mapped["Exam"] = relationship(back_populates="attempts")
    answers: Mapped[List["ExamAnswer"]] = relationship(
        "ExamAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
