from datetime import date
from typing import List

from app.modules.evaluations.models import AttendanceStatus, Evaluation
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession


async def query_evaluation_data(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: List[int] | None,
    class_ids: List[int] | None,
    student_ids: List[int] | None,
    attendance_status: List[AttendanceStatus] | None = None,
):
    query = (
        select(Evaluation)
        .order_by(asc(Evaluation.date))
        .order_by(Evaluation.class_id)
        .order_by(Evaluation.student_id)
        .where(
            Evaluation.date.between(
                date.fromisoformat(date_from), date.fromisoformat(date_to)
            )
        )
    )

    if branch_ids is not None and len(branch_ids) != 0:
        query = query.filter(Evaluation.branch_id.in_(branch_ids))

    if class_ids is not None and len(class_ids) != 0:
        query = query.filter(Evaluation.class_id.in_(class_ids))

    if student_ids is not None and len(student_ids) != 0:
        query = query.filter(Evaluation.student_id.in_(student_ids))

    if attendance_status is not None and len(attendance_status) != 0:
        query = query.filter(Evaluation.attendance_status.in_(attendance_status))

    qresult = await db.execute(query)
    return qresult.scalars().all()
