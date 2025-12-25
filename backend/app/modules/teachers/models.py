from __future__ import annotations
from datetime import datetime, date
import enum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Date, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, DateTime
from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.classes.models import Class


class EmploymentType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"


class TeacherClass(Base):
    __tablename__ = "teacher_classes"

    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_date: Mapped[date] = mapped_column(Date, default=date.today)

    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="class_links", lazy="selectin"
    )
    class_: Mapped["Class"] = relationship(
        "Class", back_populates="teacher_links", lazy="selectin"
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    qualification: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    employment_type: Mapped[Optional[EmploymentType]] = mapped_column(
        SAEnum(EmploymentType), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="teacher")
    class_links: Mapped[List["TeacherClass"]] = relationship(
        "TeacherClass",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )
    classes: Mapped[List["Class"]] = relationship(
        "Class",
        secondary="teacher_classes",
        back_populates="teachers",
    )

    def __repr__(self) -> str:
        name = getattr(self.user, "full_name", None)
        return f"<Teacher(id={self.id}, user={name})>"
