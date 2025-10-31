from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.permissions.models.permission import Permission
    from app.modules.permissions.models.permission_role import RolePermission


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )
    permission_links: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", lazy="selectin"
    )
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="role", lazy="selectin"
    )
