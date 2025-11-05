from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from app.db.base import Base
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.classes.models import Class
    from app.modules.students.models import Student
    from app.modules.users.models import User


class DailyEvaluation(Base):
    __tablename__ = "daily_evaluations"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_evaluation_student_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)

    memorization_percent: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    behavior_score: Mapped[Optional[int]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(Text)
    recorded_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    student: Mapped[Student] = relationship(
        "Student", back_populates="evaluations", lazy="selectin"
    )
    class_: Mapped[Class] = relationship(
        "Class", back_populates="daily_evaluations", lazy="selectin"
    )
    recorded_user: Mapped[Optional[User]] = relationship("User", lazy="selectin")
