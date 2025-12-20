# backend/app/modules/teachers/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status  # noqa
from app.modules.teachers.models import Teacher
from app.modules.users.models import User, UserStatus
from app.modules.classes.models import Class
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_


class TeacherCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ):
        query = (
            select(Teacher)
            .options(
                joinedload(Teacher.user).options(selectinload(User.branch_links)),
                selectinload(Teacher.classes),
            )
            .where(Teacher.user.has(User.status != UserStatus.deactive.value))
        )

        # Apply search
        if search:
            search_filter = or_(
                Teacher.user.has(User.full_name.ilike(f"%{search}%")),
                Teacher.user.has(User.email.ilike(f"%{search}%")),
            )
            query = query.where(search_filter)
        # Apply sorting
        sort_column = getattr(Teacher, sort_by) if sort_by else Teacher.id
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        result = await paginate(db, query)
        return result

    async def get_by_id(self, db: AsyncSession, teacher_id: int) -> Optional[Teacher]:
        stmt = (
            select(Teacher)
            .where(Teacher.user_id == teacher_id)
            .options(
                joinedload(Teacher.user).options(
                    selectinload(User.role),
                    selectinload(User.branches),
                    selectinload(User.branch_links),
                ),
                selectinload(Teacher.classes),
            )
            .where(Teacher.user.has(User.status != UserStatus.deactive.value))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Teacher]:
        stmt = select(Teacher).where(Teacher.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, data: dict) -> Teacher:
        teacher = Teacher(**data)
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher, attribute_names=["classes"])
        return teacher

    async def update(self, db: AsyncSession, teacher: Teacher, data: dict) -> Teacher:
        for field, value in data.items():
            setattr(teacher, field, value)
        db.add(teacher)
        await db.commit()
        # refresh teacher joined with classes
        await db.refresh(teacher, attribute_names=["classes"])
        return teacher

    async def delete(self, db: AsyncSession, teacher: Teacher) -> Teacher:
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
