from app.modules.curriculums.models.unit_item import UnitItem, UnitItemType
from app.modules.curriculums.schemas.unit_item import (
    UnitItemCreate,
    UnitItemUpdate,
)
from sqlalchemy import asc, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UnitItemCRUD:
    async def get_lesson_items(self, db: AsyncSession, unit_id: int) -> list[UnitItem]:
        query_result = await db.execute(
            select(UnitItem)
            .where(UnitItem.unit_id == unit_id, UnitItem.type == UnitItemType.LESSON)
            .order_by(asc(UnitItem.id))
        )
        return list(query_result.scalars().all())

    async def create(self, db: AsyncSession, data: UnitItemCreate) -> UnitItem:
        item = UnitItem(
            title=data.title, type=data.type, content=data.content, unit_id=data.unit_id
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    async def update(self, db: AsyncSession, id: int, data: UnitItemUpdate) -> None:
        updated_values = data.model_dump(exclude_unset=True)
        await db.execute(update(UnitItem).where(UnitItem.id == id).values(**updated_values))
        await db.commit()


unit_item_crud = UnitItemCRUD()
