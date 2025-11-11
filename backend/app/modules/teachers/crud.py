# backend/app/modules/teachers/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status  # noqa
from app.modules.teachers.models import Teacher
from app.modules.users.models import User, UserStatus


class TeacherCRUD:
    async def get_all(self, db: AsyncSession) -> List[Teacher]:
        stmt = (
            select(Teacher)
            .options(joinedload(Teacher.user), selectinload(Teacher.classes))
            .order_by(Teacher.id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, teacher_id: int) -> Optional[Teacher]:
        stmt = (
            select(Teacher)
            .where(Teacher.id == teacher_id)
            .options(joinedload(Teacher.user), selectinload(Teacher.classes))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, data: dict) -> Teacher:
        teacher = Teacher(**data)
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    async def update(self, db: AsyncSession, teacher: Teacher, data: dict) -> Teacher:
        for field, value in data.items():
            setattr(teacher, field, value)
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    async def delete(self, db: AsyncSession, teacher: Teacher) -> Teacher:
        # soft-delete via User status
        user = await db.get(User, teacher.user_id)
        if user:
            user.status = UserStatus.deactive.value
            db.add(user)
            await db.commit()
        await db.refresh(teacher)
        return teacher

    async def approve(self, db: AsyncSession, teacher: Teacher) -> Teacher:
        user = await db.get(User, teacher.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")
        user.status = UserStatus.active.value
        db.add(user)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    async def reject(self, db: AsyncSession, teacher: Teacher) -> Teacher:
        user = await db.get(User, teacher.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")
        user.status = UserStatus.rejected.value
        db.add(user)
        await db.commit()
        await db.refresh(teacher)
        return teacher


teacher_crud = TeacherCRUD()
