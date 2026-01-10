from collections.abc import Sequence
from typing import Optional

from fastapi_pagination import Page

from app.modules.curriculums.models.curriculum import Curriculum
from app.modules.curriculums.models.subject import Subject
from app.modules.curriculums.schemas.curriculum import (
    CurriculumCreate,
    CurriculumResponse,
    CurriculumUpdate,
)
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


class CurriculumCRUD:
    async def create(self, db: AsyncSession, data: CurriculumCreate) -> Curriculum:
        curriculum = Curriculum(
            name=data.name,
            description=data.description,
            academic_year=data.academic_year,
            is_active=data.is_active,
        )
        db.add(curriculum)
        await db.commit()
        await db.refresh(curriculum)
        return curriculum

    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ) -> Page[CurriculumResponse]:
        query = select(Curriculum)
        if search:
            search_term = f"%{search}%"
            query = query.where(Curriculum.name.ilike(search_term))

        sort_columns = {
            "id": Curriculum.id,
            "name": Curriculum.name,
            "description": Curriculum.description,
            "is_active": Curriculum.is_active,
        }

        safe_sort_by = sort_by or "id"
        sort_column = sort_columns.get(safe_sort_by, Curriculum.id)

        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        result = await sqlalchemy_paginate(db, query)

        return result

    async def get_subjects(self, db: AsyncSession, id: int) -> Sequence[Subject] | None:
        query_result = await db.execute(select(Curriculum).where(Curriculum.id == id))
        curriculum = query_result.scalar_one_or_none()
        if curriculum is None:
            return None

        return [link.subject for link in curriculum.subject_links]

    async def update(self, db: AsyncSession, id: int, data: CurriculumUpdate) -> None:
        updated_curriculum_values = data.model_dump(exclude_unset=True)
        await db.execute(
            update(Curriculum)
            .where(Curriculum.id == id)
            .values(**updated_curriculum_values)
        )
        await db.commit()


curriculum_crud = CurriculumCRUD()
