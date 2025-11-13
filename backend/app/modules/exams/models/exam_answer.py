from datetime import datetime
from typing import TYPE_CHECKING
from app.db.base import Base
from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .exam_attempt import ExamAttempt
    from .exam_question import ExamQuestion


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("exam_attempts.id", ondelete="CASCADE")
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("exam_questions.id", ondelete="CASCADE")
    )

    answer_text: Mapped[str] = mapped_column(Text, nullable=True)
    selected_option: Mapped[str] = mapped_column(String, nullable=True)
    marks_obtained: Mapped[float] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    attempt: Mapped["ExamAttempt"] = relationship(back_populates="answers")
    question: Mapped["ExamQuestion"] = relationship(
        back_populates="answers", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint(
            "attempt_id", "question_id", name="uq_answer_attempt_question"
        ),
    )
