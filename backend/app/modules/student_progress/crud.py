from collections.abc import Iterable, Sequence
from operator import and_

from app.modules.curriculums.models.subject_unit import SubjectUnit
from app.modules.curriculums.models.subject_unit_item import SubjectUnitItem
from app.modules.student_progress.models import StudentProgress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StudentProgressCRUD:
    async def student_get_progress(
        self, db: AsyncSession, student_id: int, subject_id: int
    ) -> Sequence[StudentProgress]:
        query_result = await db.execute(
            select(StudentProgress)
            .join(SubjectUnitItem, StudentProgress.unit_item_id == SubjectUnitItem.id)
            .join(SubjectUnit, SubjectUnitItem.unit_id == SubjectUnit.id)
            .where(
                and_(
                    StudentProgress.student_id == student_id,
                    SubjectUnit.subject_id == subject_id,
                )
            )
        )

        return query_result.scalars().all()

    async def parent_get_progress(
        self, db: AsyncSession, child_ids: Iterable[int], subject_id: int
    ) -> Sequence[StudentProgress]:
        query_result = await db.execute(
            select(StudentProgress)
            .join(SubjectUnitItem, StudentProgress.unit_item_id == SubjectUnitItem.id)
            .join(SubjectUnit, SubjectUnitItem.unit_id == SubjectUnit.id)
            .where(
                and_(
                    StudentProgress.student_id.in_(child_ids),
                    SubjectUnit.subject_id == subject_id,
                )
            )
        )

        return query_result.scalars().all()


student_progress_crud = StudentProgressCRUD()
