from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from app.db.base import Base
from sqlalchemy import JSON, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.attendance.models import Attendance
    from app.modules.branches.models import Branch  # noqa: F401
    from app.modules.classes.models import Class
    from app.modules.evaluations.models import DailyEvaluation
    from app.modules.financial.models.invoice import Invoice
    from app.modules.users.models import User  # noqa: F401


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parent_name: Mapped[str] = mapped_column(String(120))
    admission_date: Mapped[Optional[date]] = mapped_column(Date)
    curriculum_progress: Mapped[Optional[Dict]] = mapped_column(JSON)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE")
    )
    class_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("classes.id", ondelete="SET NULL")
    )

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
