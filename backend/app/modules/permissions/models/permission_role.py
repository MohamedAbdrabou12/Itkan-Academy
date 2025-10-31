# app/modules/permissions/models/permission_role.py
# app/modules/permissions/models/permission_role.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    role = relationship("Role", back_populates="permission_links", lazy="selectin")
    permission = relationship(
        "Permission", back_populates="role_links", lazy="selectin"
    )
