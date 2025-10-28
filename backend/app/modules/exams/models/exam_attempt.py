from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.exams.models.exam import Exam
    from app.modules.exams.models.exam_answer import ExamAnswer
    from app.modules.students.models import Student


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(20), default="in-progress")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    exam: Mapped[Exam] = relationship(
        "Exam", back_populates="attempts", lazy="selectin"
    )
    answers: Mapped[List[ExamAnswer]] = relationship(
        "ExamAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    student: Mapped[Student] = relationship("Student", lazy="selectin")
