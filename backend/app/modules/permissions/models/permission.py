from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.roles.models import Role


class Permission(Base):
    __tablename__ = "permissions"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Permission details
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    # Many-to-many relationship with roles through role_permissions
    roles: Mapped[List[Role]] = relationship(
        secondary="role_permissions", back_populates="permissions", lazy="selectin"
    )
