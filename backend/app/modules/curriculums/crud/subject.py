from collections.abc import Sequence

from app.modules.curriculums.models.subject import Subject
from app.modules.curriculums.models.unit import Unit
from app.modules.curriculums.schemas.subject import SubjectCreate, SubjectUpdate
from sqlalchemy import asc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class SubjectCRUD:
    async def create(self, db: AsyncSession, data: SubjectCreate) -> Subject:
        subject = Subject(name=data.name)
        db.add(subject)
        await db.commit()
        return subject

    async def get_all(self, db: AsyncSession) -> Sequence[Subject]:
        query = await db.execute(select(Subject).order_by(asc(Subject.id)))
        return query.scalars().all()

    async def get(self, db: AsyncSession, id: int) -> Subject | None:
        query = await db.execute(
            select(Subject).where(Subject.id == id).options(selectinload(Subject.units, Unit.items))
        )

        subject = query.scalar_one_or_none()
        if subject is None:
            return None

        return subject

    async def get_by_curriculum(self, db: AsyncSession, curriculum_id: int) -> Sequence[Subject]:
        query = await db.execute(
            select(Subject)
            .join(Unit, Subject.id == Unit.subject_id)
            .where(Unit.curriculum_id == curriculum_id)
            .distinct()
        )
        return query.scalars().all()

    async def update(self, db: AsyncSession, id: int, data: SubjectUpdate) -> None:
        updated_subject_values = data.model_dump(exclude_unset=True)
        await db.execute(update(Subject).where(Subject.id == id).values(**updated_subject_values))
        await db.commit()


subject_crud = SubjectCRUD()
