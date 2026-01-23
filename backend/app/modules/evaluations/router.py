from datetime import datetime, timezone
from operator import and_

from app.core.auth import get_current_user, get_current_user_id
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.evaluations.models import Evaluation
from app.modules.evaluations.schemas import (
    BulkEvaluationCreate,
    BulkEvaluationUpdate,
    ListEvaluationsResponseItem,
)
from app.modules.evaluations.services import (
    get_date_and_class,
    validate_evaluations_common,
)
from app.modules.permissions.permissions import PermissionCode
from app.modules.teachers.models import Teacher
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from .constants import EVALUATION_EDITING_TIMEFRAME
from .crud import evaluations_crud

evaluations_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@evaluations_router.get(
    "/",
    dependencies=[Depends(require_permission(PermissionCode.EVALUATION_STUDENT_VIEW))],
)
async def list_evaluations(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    evaluations = await evaluations_crud.get_all(db, current_user.id)

    return [
        ListEvaluationsResponseItem(
            id=evaluation.id,
            student_id=evaluation.student_id,
            class_id=evaluation.class_id,
            branch_id=evaluation.branch_id,
            date=evaluation.date.isoformat(),
            unit_item_id=evaluation.unit_item_id,
            unit_item_title=evaluation.unit_item.title,
            attendance_status=evaluation.attendance_status.value,
            evaluation_grades=evaluation.evaluation_grades,
            notes=evaluation.notes,
            created_at=evaluation.created_at.isoformat(),
        )
        for evaluation in evaluations
    ]


@evaluations_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.EVALUATION_STUDENT_ADD))],
)
async def bulk_create_evaluations(
    bulk_data: BulkEvaluationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            joinedload(User.role),
            selectinload(User.branches),
            selectinload(User.teacher).selectinload(Teacher.classes),
        )
    )
    result = await db.execute(stmt)
    current_user = result.scalars().unique().one()

    eval_date, class_obj = await get_date_and_class(db, bulk_data)
    student_ids_in_class = await validate_evaluations_common(db, bulk_data, current_user, eval_date, class_obj)

    # Verify previous evaluated unit item
    result = await db.execute(
        select(Evaluation.student_id).where(
            Evaluation.student_id.in_(student_ids_in_class),
            Evaluation.unit_item_id == bulk_data.unit_item_id,
        )
    )
    already_completed_ids = result.scalars().all()

    if already_completed_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"بعض الطلاب تم تقييمهم بالفعل في هذا الدرس: {already_completed_ids}",
        )

    # Check for existing evaluations for this class and date
    existing_evals = await evaluations_crud.get_all(db, current_user.id, eval_date)
    existing_student_ids = {eval.student_id for eval in existing_evals}

    already_evaluated_students = []
    for student_id in bulk_data.records.keys():
        if student_id in existing_student_ids:
            already_evaluated_students.append(student_id)

    if already_evaluated_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"تم تقييم ({class_obj.name}) في نفس التاريخ من قبل",
        )

    try:
        count = await evaluations_crud.create_bulk(
            db,
            current_user=current_user,
            eval_date=eval_date,
            branch_id=class_obj.branch_id,
            bulk_data=bulk_data,
        )
        await db.commit()
    except Exception as error:
        await db.rollback()
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطأ في إنشاء التقييمات",
        ) from error

    return {
        "message": "تم تقييم الطلاب بنجاح",
        "count": count,
        "date": eval_date.isoformat(),
        "class_id": bulk_data.class_id,
    }


@evaluations_router.put(
    "/",
    dependencies=[Depends(require_permission(PermissionCode.EVALUATION_STUDENT_EDIT))],
)
async def bulk_update_evaluations(
    bulk_data: BulkEvaluationUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.branches),
            selectinload(User.teacher).selectinload(Teacher.classes),
        )
    )
    result = await db.execute(stmt)
    current_user = result.scalars().first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    eval_date, class_obj = await get_date_and_class(db, bulk_data)
    await validate_evaluations_common(
        db,
        bulk_data,
        current_user,
        eval_date,
        class_obj,
        partial_evaluation_config=True,
    )

    existing_eval_query = select(Evaluation).where(
        and_(
            Evaluation.class_id == bulk_data.class_id,
            Evaluation.date == eval_date,
        )
    )
    existing_eval_result = await db.execute(existing_eval_query)
    existing_eval = existing_eval_result.scalar()

    if not existing_eval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يوجد تقييم لهذا الفصل ولهذا اليوم",
        )

    if (
        datetime.now(timezone.utc) - existing_eval.created_at
        > EVALUATION_EDITING_TIMEFRAME
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكنك تعديل التقييمات بعد يومين",
        )

    try:
        count = await evaluations_crud.update_bulk(db, eval_date, bulk_data.records)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطأ في تعديل التقييمات",
        )

    return {
        "message": "تم تعديل تقييمات الطلاب بنجاح",
        "count": count,
        "date": eval_date.isoformat(),
        "class_id": bulk_data.class_id,
    }
