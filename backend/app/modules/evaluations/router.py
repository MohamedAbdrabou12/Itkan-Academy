from datetime import date
from operator import and_
from typing import Any, List, Union

from app.core.auth import get_current_user
from app.db.session import get_db
from app.modules.classes.models import Class
from app.modules.evaluations.models import AttendanceStatus, Evaluation
from app.modules.evaluations.schemas import (
    BulkEvaluationCreate,
    BulkEvaluationUpdate,
    ListEvaluationsResponseItem,
)
from app.modules.users.models import User, UserStatus
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .constants import MAX_GRADE, MIN_GRADE

evaluations_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@evaluations_router.get("/", response_model=List[ListEvaluationsResponseItem])
async def list_evaluations(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(Evaluation)
        .where(Evaluation.recorded_by_user_id == current_user.id)
        .order_by(Evaluation.date)
    )
    evaluations = result.scalars().all()

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


# @evaluations_router.get("/{eval_id}", response_model=EvaluationRead)
# async def get_evaluation(
#     eval_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     evaluation = await daily_evaluation_crud.get_by_id(db, eval_id)
#     if not evaluation:
#         raise HTTPException(status_code=404, detail="Daily evaluation not found")
#     return evaluation


def validate_evaluations(
    bulk_data: Union[BulkEvaluationCreate, BulkEvaluationUpdate],
    current_user: User,
    eval_date: date,
    class_obj: Class,
    partial_evaluation_config: bool = False,
):
    role = current_user.role_name.lower() if current_user.role_name else None

    # Check branch access for all roles - USING THE CONVENIENCE RELATIONSHIP
    has_branch_access = any(
        branch.id == class_obj.branch_id for branch in current_user.branches
    )

    if not has_branch_access:
        user_branch_names = [branch.name for branch in current_user.branches]
        raise HTTPException(
            status_code=403,
            detail=f"لا يوجد صلاحية لهذا الفرع. المستخدم لديه صلاحية للأفرع: {user_branch_names}، الفصل يتطلب الفرع: {class_obj.branch.name}",
        )

    # ensure date is in class schedule
    weekday_list = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    weekday = weekday_list[eval_date.weekday()]
    if weekday not in class_obj.schedule.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{weekday.capitalize()} ليس ضمن جدول الفصل",
        )

    # ensure evaluation keys are the same as the class' evaluation config
    if not partial_evaluation_config:
        for record in bulk_data.records.values():
            if record.evaluations is None or len(record.evaluations) == 0:
                if record.attendance_status not in [
                    AttendanceStatus.ABSENT,
                    AttendanceStatus.EXCUSED,
                ]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="لا توجد تقييمات للطالب رغم عدم كونه غائب أو معذور",
                    )
                continue

            evaluation_types = map(
                lambda evaluation: evaluation.name, record.evaluations
            )
            for evaluation in class_obj.evaluation_config:
                if evaluation not in evaluation_types:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'نوع التقييم "{evaluation}" مفقود',
                    )

    # For teachers, also check class access
    if role == "teacher" and current_user.teacher:
        has_class_access = any(
            class_.id == class_obj.id for class_ in current_user.teacher.classes
        )

        if not has_class_access:
            teacher_class_names = [
                class_.name for class_ in current_user.teacher.classes
            ]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"لا يوجد صلاحية لهذا الفصل. المعلم لديه صلاحية للفصول: {teacher_class_names}، الفصل المطلوب: {class_obj.name}",
            )

    # For other non-supervisor roles, deny access
    elif role != "branch supervisor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="صلاحيات غير كافية"
        )

    # Verify all students in the request belong to the class
    student_ids_in_class = {student.id for student in class_obj.students}
    unknown_students = []
    for student_id in bulk_data.records.keys():
        if student_id not in student_ids_in_class:
            unknown_students.append(student_id)

    if unknown_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"الطلاب {unknown_students} غير مسجلين في هذا الفصل",
        )

    for student in class_obj.students:
        if student.user.status in [UserStatus.pending.value, UserStatus.rejected.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"الطالب {student.user.full_name} لم يفعل.",
            )


async def get_date_and_class(
    db: AsyncSession, bulk_data: Union[BulkEvaluationCreate, BulkEvaluationUpdate]
):
    eval_date = date.fromisoformat(bulk_data.date)

    class_query = (
        select(Class)
        .where(Class.id == bulk_data.class_id)
        .options(selectinload(Class.branch), selectinload(Class.students))
    )
    class_result = await db.execute(class_query)
    class_obj = class_result.scalar_one_or_none()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="الفصل غير موجود"
        )

    return eval_date, class_obj


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
    validate_evaluations(bulk_data, current_user, eval_date, class_obj)

    # Check for existing evaluations for this class and date
    existing_eval_query = select(Evaluation).where(
        and_(
            Evaluation.class_id == bulk_data.class_id,
            Evaluation.date == eval_date,
        )
    )
    existing_eval_result = await db.execute(existing_eval_query)
    existing_evals = existing_eval_result.scalars().all()
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

    evaluations_to_create = []

    # Ensure grades are within range and create evaluation objects
    for student_id, eval_data in bulk_data.records.items():
        evaluation_grades = []
        if eval_data.evaluations is not None:
            evaluation_grades = [
                {"name": grade.name, "grade": grade.grade}
                for grade in eval_data.evaluations
            ]

            for grade_data in evaluation_grades:
                if not (MIN_GRADE <= grade_data["grade"] <= MAX_GRADE):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"التقييم لـ {grade_data['name']} يجب أن يكون بين 0 و 10",
                    )

        evaluation = Evaluation(
            student_id=student_id,
            class_id=bulk_data.class_id,
            date=eval_date,
            recorded_by_user_id=current_user.id,
            attendance_status=AttendanceStatus(eval_data.attendance_status.value),
            evaluation_grades=evaluation_grades,
            notes=eval_data.notes,
        )
        evaluations_to_create.append(evaluation)

    if evaluations_to_create:
        try:
            db.add_all(evaluations_to_create)
            await db.commit()

            # Refresh to get the created objects with IDs
            for evaluation in evaluations_to_create:
                await db.refresh(evaluation)

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="خطأ في إنشاء التقييمات",
            )

    return {
        "message": "تم تقييم الطلاب بنجاح",
        "count": len(evaluations_to_create),
        "date": eval_date.isoformat(),
        "class_id": bulk_data.class_id,
    }


# @evaluations_router.post(
#     "/",
#     response_model=EvaluationRead,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[
#         # Depends(get_current_user),
#         # Depends(require_permission("evaluation:create")),
#     ],
# )
# async def create_evaluations(
#     eval_in: EvaluationCreate, db: AsyncSession = Depends(get_db)
# ):
#     return await daily_evaluation_crud.create(db, eval_in)


@evaluations_router.put(
    "/",
)
async def bulk_update_evaluation(
    bulk_data: BulkEvaluationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    eval_date, class_obj = await get_date_and_class(db, bulk_data)
    validate_evaluations(
        bulk_data, current_user, eval_date, class_obj, partial_evaluation_config=True
    )

    updated_evaluations = []
    for student_id, eval_data in bulk_data.records.items():
        update_dict: dict[str, Any] = {"student_id": student_id}
        if eval_data.attendance_status is not None:
            update_dict["attendance_status"] = eval_data.attendance_status

        if eval_data.notes is not None:
            update_dict["notes"] = eval_data.notes

        if eval_data.evaluations is not None:
            # TODO: check if this updates correcty
            evaluation_grades = [
                {"name": grade.name, "grade": grade.grade}
                for grade in eval_data.evaluations
            ]

            for grade_data in evaluation_grades:
                if not (MIN_GRADE <= grade_data["grade"] <= MAX_GRADE):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"التقييم لـ {grade_data['name']} يجب أن يكون بين {MIN_GRADE} و {MAX_GRADE}",
                    )

            update_dict["evaluation_grades"] = evaluation_grades

        updated_evaluations.append(update_dict)

    if updated_evaluations:
        try:
            for eval_update in updated_evaluations:
                update_values = {}
                if "attendance_status" in eval_update:
                    update_values["attendance_status"] = eval_update[
                        "attendance_status"
                    ]

                if "notes" in eval_update:
                    update_values["notes"] = eval_update["notes"]
                if "evaluation_grades" in eval_update:
                    update_values["evaluation_grades"] = eval_update[
                        "evaluation_grades"
                    ]

                if update_values:
                    await db.execute(
                        update(Evaluation)
                        .where(
                            and_(
                                Evaluation.student_id == eval_update["student_id"],
                                Evaluation.date == eval_date,
                            )
                        )
                        .values(**update_values)
                    )

            await db.commit()

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="خطأ في تعديل التقييمات",
            )

    return {
        "message": "تم تعديل تقييمات الطلاب بنجاح",
        "count": len(updated_evaluations),
        "date": eval_date.isoformat(),
        "class_id": bulk_data.class_id,
    }


# @evaluations_router.delete(
#     "/{eval_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[
#         Depends(get_current_user),
#         Depends(require_permission("evaluation:delete")),
#     ],
# )
# async def delete_evaluation(eval_id: int, db: AsyncSession = Depends(get_db)):
#     await daily_evaluation_crud.delete(db, eval_id)
#     return None
