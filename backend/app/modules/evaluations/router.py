from datetime import datetime, timezone
from operator import and_
from typing import List

from app.core.auth import get_current_user
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
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .constants import EVALUATION_EDITING_TIMEFRAME
from .crud import evaluations_crud

evaluations_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@evaluations_router.get("/", response_model=List[ListEvaluationsResponseItem])
async def list_evaluations(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    evaluations = await evaluations_crud.get_all(db, current_user.id)

    return [
        ListEvaluationsResponseItem(
            id=evaluation.id,
            student_id=evaluation.student_id,
            class_id=evaluation.class_id,
            date=evaluation.date.isoformat(),
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
)
async def bulk_create_evaluations(
    bulk_data: BulkEvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    eval_date, class_obj = await get_date_and_class(db, bulk_data)
    validate_evaluations_common(bulk_data, current_user, eval_date, class_obj)

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
            db, current_user, eval_date, bulk_data
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطأ في إنشاء التقييمات",
        )

    return {
        "message": "تم تقييم الطلاب بنجاح",
        "count": count,
        "date": eval_date.isoformat(),
        "class_id": bulk_data.class_id,
    }


@evaluations_router.put(
    "/",
)
async def bulk_update_evaluations(
    bulk_data: BulkEvaluationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    eval_date, class_obj = await get_date_and_class(db, bulk_data)
    validate_evaluations_common(
        bulk_data, current_user, eval_date, class_obj, partial_evaluation_config=True
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
