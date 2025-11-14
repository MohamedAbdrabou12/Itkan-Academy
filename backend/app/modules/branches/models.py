from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import sqlalchemy as sa

if TYPE_CHECKING:
    from app.modules.classes.models import Class
    from app.modules.users.models import User, UserBranch


class BranchStatus(Enum):
    active = "active"
    deactive = "deactive"


class Branch(Base):
    __tablename__ = "branches"
    __table_args__ = (
        sa.UniqueConstraint("name", name="uq_branches_name"),
        sa.UniqueConstraint("email", name="uq_branches_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(
        String(10), default=BranchStatus.active.value, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    classes: Mapped[List[Class]] = relationship(
        back_populates="branch", lazy="selectin", cascade="all, delete-orphan"
    )

    # Association mapped-class links (user_branches)
    user_links: Mapped[List[UserBranch]] = relationship(
        "UserBranch",
        back_populates="branch",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Convenience many-to-many relationship to users using the association table
    users_m2m: Mapped[List[User]] = relationship(
        "User",
        secondary="user_branches",
        back_populates="branches",
        lazy="selectin",
        overlaps="user_links",
    )
