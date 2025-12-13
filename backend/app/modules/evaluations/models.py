from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from app.db.base import Base
from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.branches.models import Branch
    from app.modules.classes.models import Class
    from app.modules.students.models import Student
    from app.modules.users.models import User


class AttendanceStatus(Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class Evaluation(Base):
    __tablename__ = "daily_evaluations"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "date", "class_id", name="uq_evaluation_student_class_date"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    recorded_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    attendance_status: Mapped[AttendanceStatus] = mapped_column(
        SQLEnum(AttendanceStatus), nullable=False
    )

    evaluation_grades: Mapped[List[Dict]] = mapped_column(JSONB, default=list)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    student: Mapped[Student] = relationship(
        "Student", back_populates="daily_evaluations", lazy="selectin"
    )
    class_: Mapped[Class] = relationship(
        "Class", back_populates="daily_evaluations", lazy="selectin"
    )
    branch: Mapped[Branch] = relationship("Branch", lazy="selectin")
    recorded_by_user: Mapped[User] = relationship("User", lazy="selectin")
