# app/modules/permissions/models/permission.py
# app/modules/permissions/models/permission.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.roles.models import Role
    from app.modules.permissions.models.permission_role import RolePermission


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    roles: Mapped[List[Role]] = relationship(
        secondary="role_permissions", back_populates="permissions", lazy="selectin"
    )
    role_links: Mapped[List[RolePermission]] = relationship(
        "RolePermission", back_populates="permission", lazy="selectin"
    )
