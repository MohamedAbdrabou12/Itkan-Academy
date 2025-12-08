from datetime import date
from typing import Annotated, List
from sqlalchemy import asc, select
from app.db.session import get_db
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.evaluations.models import Evaluation
from app.modules.reports.models.students import (
    StudentAttendanceReportData,
    StudentEvaluationReportData,
)

student_reports_router = APIRouter(prefix="/students")


async def query_evaluation_data(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: List[int] | None,
    class_ids: List[int] | None,
    student_ids: List[int] | None,
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

    qresult = await db.execute(query)
    return qresult.scalars().all()


@student_reports_router.get("/attendance")
async def generate_attendance_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query()] = None,
    class_ids: Annotated[List[int] | None, Query()] = None,
    student_ids: Annotated[List[int] | None, Query()] = None,
):
    evaluations = await query_evaluation_data(
        db, date_from, date_to, branch_ids, class_ids, student_ids
    )
    return [
        StudentAttendanceReportData(
            branch_id=evaluation.branch_id,
            branch_name=evaluation.branch.name,
            class_id=evaluation.class_id,
            class_name=evaluation.class_.name,
            student_id=evaluation.student_id,
            student_name=evaluation.student.user.full_name,
            date=evaluation.date.isoformat(),
            status=evaluation.attendance_status,
        )
        for evaluation in evaluations
    ]


@student_reports_router.get("/evaluations")
async def generate_evaluations_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query()] = None,
    class_ids: Annotated[List[int] | None, Query()] = None,
    student_ids: Annotated[List[int] | None, Query()] = None,
):
    evaluations = await query_evaluation_data(
        db, date_from, date_to, branch_ids, class_ids, student_ids
    )

    return [
        StudentEvaluationReportData(
            branch_id=evaluation.branch_id,
            branch_name=evaluation.branch.name,
            class_id=evaluation.class_id,
            class_name=evaluation.class_.name,
            student_id=evaluation.student_id,
            student_name=evaluation.student.user.full_name,
            date=evaluation.date.isoformat(),
            evaluation_grades=evaluation.evaluation_grades,
        )
        for evaluation in evaluations
    ]
