from datetime import date
from typing import Union

from app.modules.classes.models import Class
from app.modules.curriculums.models.unit_item import UnitItem, UnitItemType
from app.modules.evaluations.constants import MAX_GRADE, MIN_GRADE
from app.modules.evaluations.models import AttendanceStatus
from app.modules.evaluations.schemas import (
    BulkEvaluationCreate,
    BulkEvaluationUpdate,
    EvaluationGradeCreate,
    EvaluationGradeUpdate,
)
from app.modules.users.models import User, UserStatus
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def get_date_and_class(
    db: AsyncSession, bulk_data: Union[BulkEvaluationCreate, BulkEvaluationUpdate]
) -> tuple[date, Class]:
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


def check_evaluation_grades(
    evaluations: list[Union[EvaluationGradeCreate, EvaluationGradeUpdate]],
):
    evaluation_grades = [
        {"name": grade.name, "grade": grade.grade} for grade in evaluations
    ]

    for grade_data in evaluation_grades:
        if not (MIN_GRADE <= grade_data["grade"] <= MAX_GRADE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"التقييم لـ {grade_data['name']} يجب أن يكون بين {MIN_GRADE} و {MAX_GRADE}",
            )

    return evaluation_grades


async def validate_evaluations_common(
    db: AsyncSession,
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
            status_code=status.HTTP_403_FORBIDDEN,
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

    # Validate evaluations only for lesson unit items
    unit_item = await db.execute(
        select(UnitItem).where(UnitItem.id == bulk_data.unit_item_id)
    )
    unit_item = unit_item.scalar_one_or_none()

    if unit_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="الدرس غير موجود"
        )

    if unit_item.type != UnitItemType.LESSON:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يمكن تقييم الدروس فقط",
        )

    return student_ids_in_class
