from collections.abc import Iterable, Sequence
from operator import and_

from app.modules.curriculums.models.unit import Unit
from app.modules.curriculums.models.unit_item import UnitItem
from app.modules.student_progress.models import StudentProgress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StudentProgressCRUD:
    async def student_get_progress(
        self, db: AsyncSession, student_id: int, subject_id: int
    ) -> Sequence[StudentProgress]:
        query_result = await db.execute(
            select(StudentProgress)
            .join(UnitItem, StudentProgress.unit_item_id == UnitItem.id)
            .join(Unit, UnitItem.unit_id == Unit.id)
            .where(
                and_(
                    StudentProgress.student_id == student_id,
                    Unit.subject_id == subject_id,
                )
            )
        )

        return query_result.scalars().all()

    async def parent_get_progress(
        self, db: AsyncSession, child_ids: Iterable[int], subject_id: int
    ) -> Sequence[StudentProgress]:
        query_result = await db.execute(
            select(StudentProgress)
            .join(UnitItem, StudentProgress.unit_item_id == UnitItem.id)
            .join(Unit, UnitItem.unit_id == Unit.id)
            .where(
                and_(
                    StudentProgress.student_id.in_(child_ids),
                    Unit.subject_id == subject_id,
                )
            )
        )

        return query_result.scalars().all()


student_progress_crud = StudentProgressCRUD()
