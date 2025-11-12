from __future__ import annotations

from typing import TYPE_CHECKING

from app.db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.permissions.models import Permission
    from app.modules.roles.models import Role


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationship to Permission
    permission: Mapped[Permission] = relationship(
        "Permission", back_populates="role_associations", lazy="selectin"
    )

    # Relationship to Role
    role: Mapped[Role] = relationship(
        "Role", back_populates="permission_associations", lazy="selectin"
    )
