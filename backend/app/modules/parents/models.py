from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from app.db.base import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.students.models import Student


class ParentStudent(Base):
    __tablename__ = "parent_students"

    parent_id: Mapped[int] = mapped_column(
        ForeignKey("parents.id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # back_populates will be configured on both sides
    parent = relationship("Parent", back_populates="children_links", lazy="joined")
    student = relationship("Student", back_populates="parent_links", lazy="joined")


class Parent(Base):
    """
    Parent entity. Linked to a User (user_id).
    Parent is NOT branch-scoped; branches are derived from linked children
    """

    __tablename__ = "parents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    occupation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship to User
    user: Mapped["User"] = relationship("User", back_populates="parent", lazy="joined")

    # Association mapped-class links
    children_links: Mapped[List["ParentStudent"]] = relationship(
        "ParentStudent",
        back_populates="parent",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Convenience many-to-many relationship to Student
    children: Mapped[List["Student"]] = relationship(
        "Student",
        secondary="parent_students",
        back_populates="parents",
        lazy="selectin",
        viewonly=False,
    )

    def __repr__(self) -> str:
        return f"<Parent(id={self.id}, user_id={self.user_id})>"

    @property
    def branch_ids(self) -> list[int]:
        """Return unique branch ids from all children"""
        ids = set()
        for child in getattr(self, "children", []):
            ids.update(getattr(child, "branch_ids", []))
        return list(ids)

    @property
    def branches(self) -> list[dict]:
        """Return unique branches (id + name) from all children via their users."""
        all_branches = {}
        for child in getattr(self, "children", []):
            if not getattr(child, "user", None):
                continue
            for branch in getattr(child.user, "branches", []):
                all_branches[branch.id] = {"id": branch.id, "name": branch.name}
        return list(all_branches.values())
