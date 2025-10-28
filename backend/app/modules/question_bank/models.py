from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.branches.models import Branch
    from app.modules.users.models import User
    from app.modules.exams.models.exam_question import ExamQuestion
    from app.modules.exams.models.exam_answer import ExamAnswer


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    branch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE")
    )
    subject: Mapped[Optional[str]] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20), default="mcq")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[Optional[Dict]] = mapped_column(JSON)
    correct_options: Mapped[Optional[Dict]] = mapped_column(JSON)
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    branch: Mapped[Optional[Branch]] = relationship("Branch", lazy="selectin")
    creator: Mapped[Optional[User]] = relationship("User", lazy="selectin")
    exam_questions: Mapped[list[ExamQuestion]] = relationship(
        "ExamQuestion",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    exam_answers: Mapped[list[ExamAnswer]] = relationship(
        "ExamAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
