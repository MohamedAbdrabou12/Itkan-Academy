from collections.abc import Sequence

from app.modules.curriculums.models.subject_unit import SubjectUnit, SubjectUnitItem
from app.modules.curriculums.schemas.subject_unit import SubjectUnitCreate, SubjectUnitUpdate
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SubjectUnitCRUD:
    async def create(self, db: AsyncSession, data: SubjectUnitCreate) -> SubjectUnit:
        subject_unit = SubjectUnit(
            title=data.title, description=data.description, subject_id=data.subject_id
        )
        db.add(subject_unit)
        await db.commit()
        await db.refresh(subject_unit)
        return subject_unit

    async def get_items(self, db: AsyncSession, id: int) -> Sequence[SubjectUnitItem] | None:
        query_result = await db.execute(select(SubjectUnit).where(SubjectUnit.id == id))

        subject_unit = query_result.scalar_one_or_none()
        if subject_unit is None:
            return None

        return subject_unit.items

    async def update(self, db: AsyncSession, id: int, data: SubjectUnitUpdate) -> None:
        updated_values = data.model_dump(exclude_unset=True)
        await db.execute(update(SubjectUnit).where(SubjectUnit.id == id).values(**updated_values))
        await db.commit()


subject_unit_crud = SubjectUnitCRUD()
