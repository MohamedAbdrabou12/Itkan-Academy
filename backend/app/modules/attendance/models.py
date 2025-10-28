from __future__ import annotations
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import UniqueConstraint, ForeignKey, Date, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.students.models import Student
    from app.modules.classes.models import Class
    from app.modules.users.models import User


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_attendance_student_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False)
    recorded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    student: Mapped[Student] = relationship(
        "Student", back_populates="attendance_records", lazy="selectin"
    )
    class_: Mapped[Class] = relationship(
        "Class", back_populates="attendance_records", lazy="selectin"
    )
    recorded_by_user: Mapped[Optional[User]] = relationship("User", lazy="selectin")
