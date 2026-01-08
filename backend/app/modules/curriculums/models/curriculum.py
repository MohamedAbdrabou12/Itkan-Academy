from datetime import datetime
from typing import TYPE_CHECKING

from app.db.base import Base
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.classes.models import Class
    from app.modules.curriculums.models.subject import Subject

class CurriculumSubject(Base):
    __tablename__ = "curriculum_subjects"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    curriculum: Mapped["Curriculum"] = relationship(
        "Curriculum", back_populates="subject_links", lazy="selectin"
    )
    subject: Mapped["Subject"] = relationship(
        "Subject", back_populates="curriculum_links", lazy="selectin"
    )


class Curriculum(Base):
    __tablename__ = "curriculums"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    academic_year: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    subject_links: Mapped[list["CurriculumSubject"]] = relationship(
        "CurriculumSubject", back_populates="curriculum", lazy="selectin"
    )
    class_links: Mapped[list["Class"]] = relationship(
        "Class", back_populates="curriculum", lazy="selectin"
    )
