from app.modules.curriculums.models.subject_unit_item import SubjectUnitItem
from app.modules.curriculums.schemas.subject_unit_item import (
    SubjectUnitItemCreate,
    SubjectUnitItemUpdate,
)
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


class SubjectUnitItemCRUD:
    async def create(self, db: AsyncSession, data: SubjectUnitItemCreate) -> SubjectUnitItem:
        item = SubjectUnitItem(
            title=data.title, type=data.type, content=data.content, unit_id=data.unit_id
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    async def update(self, db: AsyncSession, id: int, data: SubjectUnitItemUpdate) -> None:
        updated_values = data.model_dump(exclude_unset=True)
        await db.execute(
            update(SubjectUnitItem).where(SubjectUnitItem.id == id).values(**updated_values)
        )
        await db.commit()


subject_unit_item_crud = SubjectUnitItemCRUD()
