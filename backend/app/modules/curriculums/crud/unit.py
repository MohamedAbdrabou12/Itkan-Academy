from collections.abc import Sequence
from typing import List

from app.modules.curriculums.models.unit import Unit, UnitItem
from app.modules.curriculums.schemas.unit import UnitCreate, UnitUpdate
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.classes.models import Class


class UnitCRUD:
    async def create(self, db: AsyncSession, data: UnitCreate) -> Unit:
        unit = Unit(
            title=data.title, description=data.description, subject_id=data.subject_id
        )
        db.add(unit)
        await db.commit()
        await db.refresh(unit)
        return unit

    async def get_items(self, db: AsyncSession, id: int) -> Sequence[UnitItem] | None:
        query_result = await db.execute(select(Unit).where(Unit.id == id))

        unit = query_result.scalar_one_or_none()
        if unit is None:
            return None

        return unit.items

    async def get_units_by_class(self, db: AsyncSession, class_id: int) -> List[Unit]:
        query = (
            select(Unit)
            .join(
                Class,
                (Unit.subject_id == Class.subject_id)
                & (Unit.curriculum_id == Class.curriculum_id),
            )
            .where(Class.id == class_id)
        )
        query_result = await db.execute(query)
        return list(query_result.scalars().all())

    async def update(self, db: AsyncSession, id: int, data: UnitUpdate) -> None:
        updated_values = data.model_dump(exclude_unset=True)
        await db.execute(update(Unit).where(Unit.id == id).values(**updated_values))
        await db.commit()


unit_crud = UnitCRUD()
