from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.db.base import Base
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property


if TYPE_CHECKING:
    from app.modules.permissions.models import Permission
    from app.modules.role_permissions.models import RolePermission
    from app.modules.users.models import User


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_ar: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    description_ar: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # One-to-many with User
    users: Mapped[List[User]] = relationship("User", back_populates="role")

    # Relationship through RolePermission (many-to-many)
    permission_associations: Mapped[List[RolePermission]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    # Convenience property to access permissions directly
    @property
    def permissions(self) -> List[Permission]:
        return [assoc.permission for assoc in self.permission_associations]

    @hybrid_property
    def permissions_count(self) -> int:
        if not self.permission_associations:
            return 0
        return len(self.permission_associations)
