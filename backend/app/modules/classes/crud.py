from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.modules.classes.models import Class
from app.modules.classes.schemas import ClassCreate, ClassUpdate


class ClassCRUD:
    async def get_all(self, db: AsyncSession) -> List[Class]:
        result = await db.execute(Class.__table__.select().order_by(Class.id))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, class_id: int) -> Optional[Class]:
        result = await db.get(Class, class_id)
        return result

    async def create(self, db: AsyncSession, class_in: ClassCreate) -> Class:
        class_ = Class(**class_in.dict())
        db.add(class_)
        await db.commit()
        await db.refresh(class_)
        return class_

    async def update(
        self, db: AsyncSession, class_: Class, class_in: ClassUpdate
    ) -> Class:
        for field, value in class_in.dict(exclude_unset=True).items():
            setattr(class_, field, value)
        db.add(class_)
        await db.commit()
        await db.refresh(class_)
        return class_

    async def delete(self, db: AsyncSession, class_id: int) -> None:
        class_ = await self.get_by_id(db, class_id)
        if class_:
            await db.delete(class_)
            await db.commit()


class_crud = ClassCRUD()
