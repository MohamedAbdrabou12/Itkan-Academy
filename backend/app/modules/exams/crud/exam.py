from fastapi import Request
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.modules.exams.models.exam import Exam, ExamStatus
from app.modules.exams.schemas.exam import ExamCreate, ExamUpdate
from app.modules.users.models import User
from app.modules.exams.models.exam_question import ExamQuestion
from sqlalchemy.orm import selectinload, joinedload

from fastapi_pagination.ext.sqlalchemy import paginate


class ExamCRUD:
    async def get(self, db: AsyncSession, id: int, user: User) -> Optional[Exam]:
        result = await db.execute(
            select(Exam).where(and_(Exam.id == id, Exam.created_by == user.id))
        )
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        user: User,
        request: Request,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ):
        active_branch_id = request.state.active_branch_id
        query = (
            select(Exam)
            .options(
                joinedload(Exam.questions).options(selectinload(ExamQuestion.question))
            )
            .where(and_(Exam.created_by == user.id, Exam.branch_id == active_branch_id))
        )

        # Apply search
        if search:
            query = query.where(Exam.title.ilike(f"%{search}%"))

        # Apply sorting
        sort_column = getattr(Exam, sort_by) if sort_by else Exam.id
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        result = await paginate(
            db,
            query,
        )
        return result

    async def get_by_title_and_class(
        self, db: AsyncSession, title: str, class_id: int
    ) -> Optional[Exam]:
        result = await db.execute(
            select(Exam).filter(Exam.title == title, Exam.class_id == class_id)
        )
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        obj_in: ExamCreate,
        user: User,
        active_branch_id: int,
        total_marks: int,
    ) -> Exam:
        db_obj = Exam(
            created_by=user.id,
            branch_id=active_branch_id,
            title=obj_in.title,
            duration_minutes=obj_in.duration_minutes,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            class_id=obj_in.class_id,
            total_marks=total_marks,
            status=ExamStatus.DRAFT,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Exam, obj_in: ExamUpdate, total_marks: int
    ):
        # exculde questions from obj_in
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        if "questions" in obj_in_data:
            obj_in_data.pop("questions")

        update_data = obj_in_data
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.total_marks = total_marks

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
