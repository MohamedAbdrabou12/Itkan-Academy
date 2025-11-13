# backend/app/modules/users/models.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from app.db.base import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.notifications.models import Notification
    from app.modules.roles.models import Role
    from app.modules.branches.models import Branch
    from app.modules.students.models import Student
    from app.modules.teachers.models import Teacher
    from app.modules.exams.models.exam_attempt import ExamAttempt


class UserStatus(Enum):
    pending = "pending"
    active = "active"
    rejected = "rejected"
    deactive = "deactive"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    branch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        String(20), default=UserStatus.pending, nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    role: Mapped[Optional[Role]] = relationship(
        "Role", back_populates="users", lazy="joined"
    )
    branch: Mapped[Optional[Branch]] = relationship(
        "Branch", back_populates="users", lazy="joined"
    )
    notifications: Mapped[List[Notification]] = relationship(
        "Notification",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    student: Mapped[Optional[Student]] = (  # One-to-one relationship with Student
        relationship("Student", back_populates="user", uselist=False)
    )
    teacher: Mapped[Optional[Teacher]] = (  # One-to-one relationship with Teacher
        relationship("Teacher", back_populates="user", uselist=False)
    )
    exam_attempts: Mapped[List[ExamAttempt]] = relationship(
        "ExamAttempt", back_populates="student", lazy="selectin"
    )

    # Computed attributes (not stored in DB)
    @property
    def role_name(self) -> Optional[str]:
        return self.role.name if self.role else None

    @property
    def branch_name(self) -> Optional[str]:
        return self.branch.name if self.branch else None

    @property
    def permission_code(self) -> Optional[str]:
        return self.role.permission_code if self.role else None

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}')>"
