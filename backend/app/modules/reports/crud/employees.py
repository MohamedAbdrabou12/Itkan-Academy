from datetime import date
from typing import List, Optional
from sqlalchemy import select, and_, not_
from sqlalchemy.orm import selectinload
from app.modules.attendance.models import AttendanceDaily
from app.modules.users.models import User
from app.modules.teachers.models import Teacher, TeacherClass
from app.modules.staff_evaluations.models import EmployeeEvaluation, EvaluationStatus
from sqlalchemy.ext.asyncio import AsyncSession

async def query_teacher_attendance_data(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: Optional[List[int]] = None,
    class_ids: Optional[List[int]] = None,
    teacher_ids: Optional[List[int]] = None,
):
    query = (
        select(AttendanceDaily)
        .join(User, User.id == AttendanceDaily.user_id)
        .where(User.teacher.has())
        .where(
            AttendanceDaily.date.between(
                date.fromisoformat(date_from), date.fromisoformat(date_to)
            )
        )
        .options(
            selectinload(AttendanceDaily.user).selectinload(User.teacher).selectinload(Teacher.classes),
            selectinload(AttendanceDaily.user).selectinload(User.role),
            selectinload(AttendanceDaily.branch)
        )
        .order_by(AttendanceDaily.date.asc(), AttendanceDaily.user_id.asc())
    )

    if branch_ids is not None and len(branch_ids) != 0:
        query = query.filter(AttendanceDaily.branch_id.in_(branch_ids))

    if teacher_ids is not None and len(teacher_ids) != 0:
        query = query.filter(AttendanceDaily.user_id.in_(teacher_ids))

    if class_ids is not None and len(class_ids) != 0:
        query = query.join(Teacher, Teacher.user_id == User.id)\
                     .join(TeacherClass, TeacherClass.teacher_id == Teacher.id)\
                     .filter(TeacherClass.class_id.in_(class_ids))

    result = await db.execute(query)
    return result.scalars().unique().all()

async def query_staff_attendance_data(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: Optional[List[int]] = None,
    staff_ids: Optional[List[int]] = None,
):
    query = (
        select(AttendanceDaily)
        .join(User, User.id == AttendanceDaily.user_id)
        .where(
            and_(
                not_(User.teacher.has()),
                not_(User.student.has()),
                not_(User.parent.has()),
            )
        )
        .where(
            AttendanceDaily.date.between(
                date.fromisoformat(date_from), date.fromisoformat(date_to)
            )
        )
        .options(
            selectinload(AttendanceDaily.user).selectinload(User.role),
            selectinload(AttendanceDaily.branch)
        )
        .order_by(AttendanceDaily.date.asc(), AttendanceDaily.user_id.asc())
    )

    if branch_ids is not None and len(branch_ids) != 0:
        query = query.filter(AttendanceDaily.branch_id.in_(branch_ids))

    if staff_ids is not None and len(staff_ids) != 0:
        query = query.filter(AttendanceDaily.user_id.in_(staff_ids))

    result = await db.execute(query)
    return result.scalars().unique().all()

async def get_latest_evaluation_scores(db: AsyncSession, user_ids: List[int]) -> dict[int, EmployeeEvaluation]:
    if not user_ids:
        return {}
    
    query = (
        select(EmployeeEvaluation)
        .where(EmployeeEvaluation.employee_user_id.in_(user_ids))
        .where(EmployeeEvaluation.status == EvaluationStatus.approved)
        .options(selectinload(EmployeeEvaluation.evaluator))
        .order_by(EmployeeEvaluation.employee_user_id, EmployeeEvaluation.created_at.desc())
    )
    result = await db.execute(query)
    evaluations = result.scalars().all()
    
    latest_evals = {}
    for eval_rec in evaluations:
        if eval_rec.employee_user_id not in latest_evals:
            latest_evals[eval_rec.employee_user_id] = eval_rec
    return latest_evals
