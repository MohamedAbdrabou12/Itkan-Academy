from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.branches.models import Branch  # noqa: F401
    from app.modules.students.models import Student  # noqa: F401
    from app.modules.attendance.models import Attendance  # noqa: F401
    from app.modules.evaluations.models.daily_evaluation import DailyEvaluation  # noqa: F401


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    schedule: Mapped[Optional[Dict]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    branch: Mapped[Branch] = relationship(
        "Branch", back_populates="classes", lazy="selectin"
    )
    students: Mapped[List[Student]] = relationship(
        "Student", back_populates="class_", lazy="selectin"
    )
    attendance_records: Mapped[List[Attendance]] = relationship(
        "Attendance", back_populates="class_", lazy="selectin"
    )
    daily_evaluations: Mapped[List[DailyEvaluation]] = relationship(
        "DailyEvaluation", back_populates="class_", lazy="selectin"
    )
