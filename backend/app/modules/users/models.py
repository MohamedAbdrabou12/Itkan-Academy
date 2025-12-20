from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from app.db.base import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.branches.models import Branch
    from app.modules.exams.models.exam_attempt import ExamAttempt
    from app.modules.notifications.models import Notification
    from app.modules.roles.models import Role
    from app.modules.students.models import Student
    from app.modules.teachers.models import Teacher
    from app.modules.parents.models import Parent


class UserStatus(str, Enum):
    pending = "pending"
    active = "active"
    rejected = "rejected"
    deactive = "deactive"


class UserBranch(Base):
    __tablename__ = "user_branches"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="branch_links",
    )
    branch = relationship("Branch", back_populates="user_links")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(
        String(120), unique=True, nullable=True, index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=UserStatus.pending.value, nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    login_identifier: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    login_type: Mapped[str] = mapped_column(String(20), nullable=False)

    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="users")

    branch_links: Mapped[List["UserBranch"]] = relationship(
        "UserBranch",
        back_populates="user",
        viewonly=True,
    )

    branches: Mapped[List["Branch"]] = relationship(
        "Branch",
        secondary="user_branches",
        back_populates="users_m2m",
        viewonly=True,
    )

    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student: Mapped[Optional["Student"]] = relationship(
        "Student", back_populates="user", uselist=False
    )
    teacher: Mapped[Optional["Teacher"]] = relationship(
        "Teacher", back_populates="user", uselist=False
    )
    exam_attempts: Mapped[List[ExamAttempt]] = relationship(
        "ExamAttempt", back_populates="student"
    )
    parent: Mapped[Optional["Parent"]] = relationship(
        "Parent", back_populates="user", uselist=False
    )

    @property
    def role_name(self) -> Optional[str]:
        return self.role.name if self.role else None

    @property
    def role_name_ar(self) -> Optional[str]:
        return self.role.name_ar if self.role else None

    @property
    def branch_name(self) -> Optional[str]:
        return self.branches[0].name if self.branches else None

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.full_name}')>"
