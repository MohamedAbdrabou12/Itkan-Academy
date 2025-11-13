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
    from app.modules.staff.models import Staff


class UserStatus(Enum):
    pending = "pending"
    active = "active"
    rejected = "rejected"
    deactive = "deactive"


class UserBranch(Base):
    """
    Association table mapping users <-> branches (many-to-many).
    Using a mapped-class allows adding extra fields later (role_in_branch, joined_at, etc.)
    """

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

    # relationships (optional convenience backrefs)
    user = relationship("User", back_populates="branch_links", lazy="selectin")
    branch = relationship("Branch", back_populates="user_links", lazy="selectin")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
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

    # Relationships
    role: Mapped[Optional["Role"]] = relationship(
        "Role", back_populates="users", lazy="joined"
    )

    # association mapped-class links (user_branches)
    branch_links: Mapped[List["UserBranch"]] = relationship(
        "UserBranch",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # convenience many-to-many relationship to branches using the association table
    branches: Mapped[List["Branch"]] = relationship(
        "Branch",
        secondary="user_branches",
        back_populates="users",
        lazy="selectin",
    )

    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    student: Mapped[Optional["Student"]] = relationship(
        "Student", back_populates="user", uselist=False
    )
    teacher: Mapped[Optional["Teacher"]] = relationship(
        "Teacher", back_populates="user", uselist=False
    )
    staff: Mapped[Optional["Staff"]] = relationship(
        "Staff",
        back_populates="user",
        uselist=False,
        lazy="joined",
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
