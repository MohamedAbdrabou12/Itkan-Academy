from typing import TYPE_CHECKING

from app.db.base import Base
from app.modules.curriculums.models.unit_item import UnitItem
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.curriculums.models.subject import Subject


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )

    subject: Mapped["Subject"] = relationship("Subject", back_populates="units", lazy="selectin")
    items: Mapped[list[UnitItem]] = relationship(
        "UnitItem", back_populates="unit", lazy="selectin"
    )
