from collections.abc import Sequence

from app.modules.curriculums.models.curriculum import Curriculum
from app.modules.curriculums.models.subject import Subject
from app.modules.curriculums.models.subject_unit import SubjectUnit
from app.modules.curriculums.schemas.subject import SubjectCreate, SubjectUpdate
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SubjectCRUD:
    async def create(self, db: AsyncSession, data: SubjectCreate) -> Subject:
        subject = Subject(name=data.name)
        db.add(subject)
        await db.commit()
        return subject

    async def get_all(self, db: AsyncSession) -> Sequence[Subject]:
        query = await db.execute(select(Subject))
        return query.scalars().all()

    async def get_curriculums(self, db: AsyncSession, id: int) -> Sequence[Curriculum] | None:
        query = await db.execute(select(Subject).where(Subject.id == id))

        subject = query.scalar_one_or_none()
        if not subject:
            return None

        return [link.curriculum for link in subject.curriculum_links]

    async def get_units(self, db: AsyncSession, id: int) -> Sequence[SubjectUnit] | None:
        query = await db.execute(select(Subject).where(Subject.id == id))

        subject = query.scalar_one_or_none()
        if subject is None:
            return None

        return subject.units

    async def update(self, db: AsyncSession, id: int, data: SubjectUpdate) -> None:
        updated_subject_values = data.model_dump(exclude_unset=True)
        await db.execute(update(Subject).where(Subject.id == id).values(**updated_subject_values))
        await db.commit()


subject_crud = SubjectCRUD()
