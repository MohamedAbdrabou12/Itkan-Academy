from collections.abc import Sequence

from app.modules.curriculums.models.curriculum import Curriculum
from app.modules.curriculums.models.subject import Subject
from app.modules.curriculums.schemas.curriculum import CurriculumCreate, CurriculumUpdate
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class CurriculumCRUD:
    async def create(self, db: AsyncSession, data: CurriculumCreate) -> Curriculum:
        curriculum = Curriculum(
            name=data.name,
            description=data.description,
            academic_year=data.academic_year,
            is_active=True,
        )
        db.add(curriculum)
        await db.commit()
        await db.refresh(curriculum)
        return curriculum

    async def get_all(self, db: AsyncSession) -> Sequence[Curriculum]:
        query_result = await db.execute(select(Curriculum))
        return query_result.scalars().all()

    async def get_subjects(self, db: AsyncSession, id: int) -> Sequence[Subject] | None:
        query_result = await db.execute(select(Curriculum).where(Curriculum.id == id))
        curriculum = query_result.scalar_one_or_none()
        if curriculum is None:
            return None

        return [link.subject for link in curriculum.subject_links]

    async def update(self, db: AsyncSession, id: int, data: CurriculumUpdate) -> None:
        updated_curriculum_values = data.model_dump(exclude_unset=True)
        await db.execute(
            update(Curriculum).where(Curriculum.id == id).values(**updated_curriculum_values)
        )
        await db.commit()


curriculum_crud = CurriculumCRUD()
