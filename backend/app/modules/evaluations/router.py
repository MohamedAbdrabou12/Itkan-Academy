from datetime import date
from operator import and_

from app.core.auth import get_current_user
from app.db.session import get_db
from app.modules.classes.models import Class
from app.modules.evaluations.models import AttendanceStatus, Evaluation
from app.modules.evaluations.schemas import BulkEvaluationCreate
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .constants import MAX_GRADE, MIN_GRADE

evaluations_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


# @evaluations_router.get("/", response_model=List[EvaluationRead])
# async def list_evaluations(
#     db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
# ):
#     return await daily_evaluation_crud.get_all(db)


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


@evaluations_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_bulk_evaluations(
    bulk_data: BulkEvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(bulk_data.date, '🔥')
    eval_date = date.fromisoformat(bulk_data.date)

    # Get class with relationships
    class_query = (
        select(Class)
        .where(Class.id == bulk_data.class_id)
        .options(selectinload(Class.branch), selectinload(Class.students))
    )
    class_result = await db.execute(class_query)
    class_obj = class_result.scalar_one_or_none()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # DEBUG
    print(f"User branches: {[b.id for b in current_user.branches]}")
    print(f"Class branch_id: {class_obj.branch_id}")

    # Permission checks
    role = current_user.role_name.lower() if current_user.role_name else None

    # Check branch access for all roles - USING THE CONVENIENCE RELATIONSHIP
    has_branch_access = any(
        branch.id == class_obj.branch_id for branch in current_user.branches
    )

    if not has_branch_access:
        user_branch_ids = [branch.id for branch in current_user.branches]
        raise HTTPException(
            status_code=403,
            detail=f"No access to this branch. User has access to branches: {user_branch_ids}, class requires branch: {class_obj.branch_id}",
        )
    
    # TODO: ensure date is in class schedule

    # For teachers, also check class access - USING THE CONVENIENCE RELATIONSHIP
    if role == "teacher" and current_user.teacher:
        has_class_access = any(
            class_.id == class_obj.id for class_ in current_user.teacher.classes
        )

        if not has_class_access:
            teacher_class_ids = [class_.id for class_ in current_user.teacher.classes]
            raise HTTPException(
                status_code=403,
                detail=f"No access to this class. Teacher has access to classes: {teacher_class_ids}, requested class: {class_obj.id}",
            )

    # For other non-supervisor roles, deny access
    elif role != "branch supervisor":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Verify all students in the request belong to the class
    student_ids_in_class = {student.id for student in class_obj.students}
    missing_students = []
    for student_id in bulk_data.records.keys():
        if student_id not in student_ids_in_class:
            missing_students.append(student_id)

    if missing_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Students {missing_students} are not in this class",
        )

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

    # Check if any student already has evaluation for this date
    already_evaluated_students = []
    for student_id in bulk_data.records.keys():
        if student_id in existing_student_ids:
            already_evaluated_students.append(student_id)

    if already_evaluated_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Students {already_evaluated_students} already evaluated for this date",
        )

    evaluations_to_create = []

    for student_id, eval_data in bulk_data.records.items():
        # Handle evaluations - use empty list if None
        evaluation_grades = []
        if eval_data.evaluations is not None:
            evaluation_grades = [
                {"name": grade.name, "grade": grade.grade}
                for grade in eval_data.evaluations
            ]

            # Validate grades are within range (0-10)
            for grade_data in evaluation_grades:
                if not (MIN_GRADE <= grade_data["grade"] <= MAX_GRADE):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Grade for {grade_data['name']} must be between 0 and 10",
                    )

        # Create evaluation object
        evaluation = Evaluation(
            student_id=student_id,
            class_id=bulk_data.class_id,
            date=eval_date,
            recorded_by_user_id=current_user.id,
            attendance_status=AttendanceStatus(eval_data.status.value),
            evaluation_grades=evaluation_grades,
            notes=eval_data.notes,
        )
        evaluations_to_create.append(evaluation)

    # Bulk create evaluations
    if evaluations_to_create:
        try:
            db.add_all(evaluations_to_create)
            await db.commit()

            # Refresh to get the created objects with IDs
            for evaluation in evaluations_to_create:
                await db.refresh(evaluation)

        except Exception as e:
            await db.rollback()
            # Log the actual error for debugging
            print(f"Error creating evaluations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating evaluations",
            )

    return {
        "message": "Evaluations created successfully",
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


# @evaluations_router.put(
#     "/{eval_id}",
#     response_model=EvaluationRead,
#     dependencies=[
#         Depends(get_current_user),
#         Depends(require_permission("evaluation:update")),
#     ],
# )
# async def update_evaluation(
#     eval_id: int, eval_in: EvaluationUpdate, db: AsyncSession = Depends(get_db)
# ):
#     evaluation = await daily_evaluation_crud.get_by_id(db, eval_id)
#     if not evaluation:
#         raise HTTPException(status_code=404, detail="Daily evaluation not found")
#     return await daily_evaluation_crud.update(db, evaluation, eval_in)


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
