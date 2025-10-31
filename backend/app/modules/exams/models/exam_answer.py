# app/modules/exams/models/exam_answer.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.exams.models.exam_attempt import ExamAttempt
    from app.modules.question_bank.models import QuestionBank  # adjust path if needed


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("question_bank.id", ondelete="CASCADE"), nullable=False
    )
    chosen_option: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    attempt: Mapped[ExamAttempt] = relationship(
        "ExamAttempt", back_populates="answers", lazy="selectin"
    )
    question: Mapped[QuestionBank] = relationship("QuestionBank", lazy="selectin")
