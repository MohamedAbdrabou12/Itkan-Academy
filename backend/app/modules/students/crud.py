# backend/app/modules/students/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import or_, asc, desc
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from app.modules.students.models import Student, StudentClass
from app.modules.users.models import User


class StudentCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ):
        stmt = select(Student).options(
            selectinload(Student.classes), joinedload(Student.user)
        )

        if search:
            search_term = f"%{search}%"
            stmt = stmt.join(Student.user).where(
                or_(User.full_name.ilike(search_term), User.email.ilike(search_term))
            )

        if status:
            stmt = stmt.join(Student.user).where(User.status == status)

        sort_columns = {
            "id": Student.id,
            "admission_date": Student.admission_date,
            "full_name": User.full_name,
            "email": User.email,
            "status": User.status,
        }

        sort_column = sort_columns.get(sort_by, Student.id)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))

        return await sqlalchemy_paginate(db, stmt)

    async def get_by_id(self, db: AsyncSession, student_id: int) -> Optional[Student]:
        stmt = (
            select(Student)
            .where(Student.id == student_id)
            .options(selectinload(Student.classes), joinedload(Student.user))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Student]:
        stmt = select(Student).where(Student.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, student_payload: dict) -> Student:
        student = Student(**student_payload)
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    async def update(self, db: AsyncSession, student: Student, data: dict) -> Student:
        for field, value in data.items():
            setattr(student, field, value)
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    async def delete(self, db: AsyncSession, student: Student) -> None:
        await db.delete(student)
        await db.commit()

    async def update_student_classes(
        self, db: AsyncSession, student: Student, class_ids: List[int]
    ):
        from sqlalchemy import delete

        await db.execute(
            delete(StudentClass).where(StudentClass.student_id == student.id)
        )
        for cid in class_ids:
            db.add(StudentClass(student_id=student.id, class_id=cid))
        await db.commit()
        await db.refresh(student)


student_crud = StudentCRUD()
