from collections.abc import Sequence
from datetime import date
from operator import and_
from typing import Any

from app.modules.evaluations.models import Evaluation
from app.modules.evaluations.schemas import (
    BulkEvaluationCreate,
    StudentEvaluationUpdate,
)
from app.modules.evaluations.services import check_evaluation_grades
from app.modules.student_progress.models import StudentProgress
from app.modules.users.models import User
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class DailyEvaluationCRUD:
    async def get_all(
        self, db: AsyncSession, recorded_by_user_id: int, date: date | None = None
    ) -> Sequence[Evaluation]:
        query = select(Evaluation).where(Evaluation.recorded_by_user_id == recorded_by_user_id)

        if date is not None:
            query = query.where(Evaluation.date == date)

        query = query.order_by(Evaluation.date)

        result = await db.execute(query)
        return result.scalars().all()

    async def create_bulk(
        self,
        db: AsyncSession,
        current_user: User,
        eval_date: date,
        branch_id: int,
        bulk_data: BulkEvaluationCreate,
    ) -> int:
        evaluations_to_create = []

        # Ensure grades are within range and create evaluation objects
        for student_id, eval_data in bulk_data.records.items():
            evaluation_grades = []
            if eval_data.evaluations is not None:
                evaluation_grades = check_evaluation_grades(eval_data.evaluations)

            evaluation = Evaluation(
                student_id=student_id,
                class_id=bulk_data.class_id,
                branch_id=branch_id,
                date=eval_date,
                recorded_by_user_id=current_user.id,
                attendance_status=eval_data.attendance_status,
                evaluation_grades=evaluation_grades,
                notes=eval_data.notes,
            )
            evaluations_to_create.append(evaluation)

        if evaluations_to_create:
            db.add_all(evaluations_to_create)
            await db.commit()

            progress_to_create = []
            for evaluation in evaluations_to_create:
                await db.refresh(evaluation)
                progress_to_create.append(
                    StudentProgress(
                        student_id=evaluation.student_id,
                        unit_item_id=bulk_data.unit_item_id,
                        evaluation_id=evaluation.id,
                    )
                )

        return len(evaluations_to_create)

    async def update_bulk(
        self,
        db: AsyncSession,
        eval_date: date,
        records: dict[int, StudentEvaluationUpdate],
    ) -> int:
        updated_evaluations = []
        for student_id, eval_data in records.items():
            update_dict: dict[str, Any] = {"student_id": student_id}
            if eval_data.attendance_status is not None:
                update_dict["attendance_status"] = eval_data.attendance_status

            if eval_data.notes is not None:
                update_dict["notes"] = eval_data.notes

            if eval_data.evaluations is not None:
                evaluation_grades = check_evaluation_grades(eval_data.evaluations)
                update_dict["evaluation_grades"] = evaluation_grades

            updated_evaluations.append(update_dict)

        if updated_evaluations:
            for eval_update in updated_evaluations:
                await db.execute(
                    update(Evaluation)
                    .where(
                        and_(
                            Evaluation.student_id == eval_update["student_id"],
                            Evaluation.date == eval_date,
                        )
                    )
                    .values(**eval_update)
                )

        return len(updated_evaluations)


evaluations_crud = DailyEvaluationCRUD()
