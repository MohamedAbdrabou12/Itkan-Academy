from app.modules.curriculums.models.curriculum import Curriculum
from app.modules.curriculums.schemas.curriculum import (
    CurriculumCreate,
    CurriculumResponse,
    CurriculumUpdate,
)
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import asc, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession


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
        search: str | None = None,
        sort_by: str | None = "id",
        sort_order: str | None = "asc",
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

        return await sqlalchemy_paginate(db, query)

    async def update(self, db: AsyncSession, id: int, data: CurriculumUpdate) -> None:
        updated_curriculum_values = data.model_dump(exclude_unset=True)
        await db.execute(
            update(Curriculum).where(Curriculum.id == id).values(**updated_curriculum_values)
        )
        await db.commit()


curriculum_crud = CurriculumCRUD()
