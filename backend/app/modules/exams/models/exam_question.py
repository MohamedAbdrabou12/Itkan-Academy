# app/modules/exams/models/exam_question.py
from __future__ import annotations
from datetime import datetime  # noqa E401
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.exams.models import Exam
    from app.modules.question_bank.models import QuestionBank  # adjust path if needed


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    # Composite primary key: exam_id + question_id
    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("question_bank.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    # Order of the question within the exam
    question_order: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    exam: Mapped[Exam] = relationship("Exam", back_populates="questions", lazy="joined")
    question: Mapped[QuestionBank] = relationship("QuestionBank", lazy="joined")
