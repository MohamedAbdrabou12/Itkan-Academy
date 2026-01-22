from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional

from app.db.base import Base
from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.branches.models import Branch
    from app.modules.users.models import User


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionOptions(str, Enum):
    OPTION_A = "A"
    OPTION_B = "B"
    OPTION_C = "C"
    OPTION_D = "D"
    OPTION_E = "E"
    OPTION_F = "F"


class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String(100))

    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        String(20), default=QuestionDifficulty.MEDIUM
    )

    options: Mapped[Optional[list[dict[str, str]]]] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[Optional[QuestionOptions]] = mapped_column(
        String(20), nullable=True
    )

    branch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE")
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    type: Mapped[QuestionType] = mapped_column(String(20), default=QuestionType.MCQ)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    is_shared: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        UniqueConstraint("title", "created_by", name="uq_title_created_by"),
    )

    # Relationships
    branch: Mapped[Branch] = relationship("Branch")
    creator: Mapped[Optional[User]] = relationship("User")
