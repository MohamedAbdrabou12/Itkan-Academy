# app/modules/users/models.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.roles.models import Role
    from app.modules.branches.models import Branch
    from app.modules.notifications.models import Notification


class UserStatus(str, Enum):
    pending = "pending"
    active = "active"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL")
    )
    branch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL")
    )

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[UserStatus] = mapped_column(
        String(20), default=UserStatus.pending, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Two-factor authentication enabled
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    role: Mapped[Optional[Role]] = relationship(
        "Role", back_populates="users", lazy="joined"
    )
    branch: Mapped[Optional[Branch]] = relationship(
        "Branch", back_populates="users", lazy="joined"
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
