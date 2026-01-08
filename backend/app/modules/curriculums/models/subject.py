from datetime import datetime

from app.db.base import Base
from app.modules.classes.models import Class
from app.modules.curriculums.models.curriculum import CurriculumSubject
from app.modules.curriculums.models.subject_unit import SubjectUnit
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    curriculum_links: Mapped[list[CurriculumSubject]] = relationship(
        "CurriculumSubject",
        back_populates="subject",
        lazy="selectin",
    )
    class_links: Mapped[list[Class]] = relationship(
        "Class", back_populates="subject", lazy="selectin"
    )
    units: Mapped[list[SubjectUnit]] = relationship(
        "SubjectUnit", back_populates="subject", lazy="selectin"
    )
