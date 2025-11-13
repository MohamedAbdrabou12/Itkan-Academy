from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.modules.exams.models.exam import Exam, ExamStatus
from app.modules.exams.schemas.exam import ExamCreate, ExamUpdate
from app.modules.users.models import User


class ExamCRUD:
    async def get(self, db: AsyncSession, id: int, user: User) -> Optional[Exam]:
        result = await db.execute(
            select(Exam).where(and_(Exam.id == id, Exam.created_by == user.id))
        )
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, user: User):
        result = await db.execute(select(Exam).where(Exam.created_by == user.id))
        return result.scalars().all()

    async def get_by_title_and_class(
        self, db: AsyncSession, title: str, class_id: int
    ) -> Optional[Exam]:
        result = await db.execute(
            select(Exam).filter(Exam.title == title, Exam.class_id == class_id)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: ExamCreate, user: User) -> Exam:
        db_obj = Exam(
            **obj_in.model_dump(),
            created_by=user.id,
            branch_id=user.branch_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Exam, obj_in: ExamUpdate) -> Exam:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int, user: User) -> Optional[Exam]:
        result = await db.execute(
            select(Exam).where(and_(Exam.id == id, Exam.created_by == user.id))
        )
        db_obj = result.scalars().first()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj

    async def publich_exam(self, db: AsyncSession, db_obj: Exam) -> Exam:
        db_obj.status = ExamStatus.PUBLISHED
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def close_exam(self, db: AsyncSession, db_obj: Exam):
        db_obj.status = ExamStatus.CLOSED
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_total_marks(
        self, db: AsyncSession, db_obj: Exam, total_marks: int
    ) -> Exam:
        db_obj.total_marks = total_marks
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


exam_crud = ExamCRUD()
