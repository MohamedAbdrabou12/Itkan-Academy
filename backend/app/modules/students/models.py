from __future__ import annotations
from datetime import date, datetime
from typing import Optional, List, Dict, TYPE_CHECKING

from sqlalchemy import String, JSON, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.users.models import User  # noqa: F401
    from app.modules.branches.models import Branch  # noqa: F401
    from app.modules.classes.models import Class
    from app.modules.attendance.models import Attendance
    from app.modules.evaluations.models.daily_evaluation import DailyEvaluation
    from app.modules.financial.models.invoice import Invoice


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    parent_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE")
    )
    class_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("classes.id", ondelete="SET NULL")
    )

    admission_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="active")
    curriculum_progress: Mapped[Optional[Dict]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    class_: Mapped[Optional[Class]] = relationship(
        "Class", back_populates="students", lazy="joined"
    )
    attendance_records: Mapped[List[Attendance]] = relationship(
        "Attendance", back_populates="student", lazy="selectin"
    )
    evaluations: Mapped[List[DailyEvaluation]] = relationship(
        "DailyEvaluation", back_populates="student", lazy="selectin"
    )
    invoices: Mapped[List[Invoice]] = relationship(
        "Invoice", back_populates="student", lazy="selectin"
    )
