import datetime
from typing import TYPE_CHECKING, final

from app.db.base import Base
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.classes.models import Class


@final
class Curriculum(Base):
    __tablename__ = "curriculums"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    academic_year: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    class_links: Mapped[list["Class"]] = relationship(
        "Class", back_populates="curriculum", lazy="selectin"
    )
