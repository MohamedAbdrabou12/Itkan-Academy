from enum import Enum
from typing import TYPE_CHECKING

from app.db.base import Base
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.curriculums.models.unit import Unit


class UnitItemType(Enum):
    LESSON = "lesson"
    EXAM = "exam"
    VIDEO = "video"


class UnitItem(Base):
    __tablename__ = "unit_items"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    type: Mapped["UnitItemType"] = mapped_column(SQLEnum(UnitItemType), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), nullable=False)

    unit: Mapped["Unit"] = relationship("Unit", back_populates="items", lazy="selectin")
