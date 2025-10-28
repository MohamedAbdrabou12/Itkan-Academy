from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.branches.models import Branch
    from app.modules.classes.models import Class
    from app.modules.users.models import User
    from app.modules.exams.models.exam_question import ExamQuestion
    from app.modules.exams.models.exam_attempt import ExamAttempt


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)

    branch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL")
    )
    class_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("classes.id", ondelete="SET NULL")
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    start_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    branch: Mapped[Optional[Branch]] = relationship("Branch", lazy="joined")
    class_: Mapped[Optional[Class]] = relationship("Class", lazy="joined")
    creator: Mapped[Optional[User]] = relationship("User", lazy="joined")
    questions: Mapped[List[ExamQuestion]] = relationship(
        "ExamQuestion", back_populates="exam", lazy="selectin"
    )
    attempts: Mapped[List[ExamAttempt]] = relationship(
        "ExamAttempt", back_populates="exam", lazy="selectin"
    )
