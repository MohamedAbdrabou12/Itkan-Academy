# app/modules/branches/models.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.classes.models import Class


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    users: Mapped[List[User]] = relationship(
        back_populates="branch", lazy="selectin", cascade="all, delete-orphan"
    )
    classes: Mapped[List[Class]] = relationship(
        back_populates="branch", lazy="selectin", cascade="all, delete-orphan"
    )
