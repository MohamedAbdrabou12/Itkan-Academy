from datetime import date
from operator import and_

from sqlalchemy import select

from app.core.auth import get_current_user
from app.db.session import get_db
from app.modules.classes.models import Class
from app.modules.evaluations.schemas import BulkEvaluationCreate
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.evaluations.models import AttendanceStatus, Evaluation

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
    eval_date = date.fromisoformat(bulk_data.date)

    class_query = select(Class).where(Class.id == bulk_data.class_id)
    class_result = await db.execute(class_query)
    class_obj = class_result.scalar_one_or_none()

    permission_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have access to this class",
    )

    if not class_obj:
        raise permission_exception

    role = current_user.role_name.lower() if current_user.role_name else None
    if role == "teacher" and current_user.teacher:
        for class_ in current_user.teacher.classes:
            if class_.id == class_obj.id:
                break
        else:
            raise permission_exception
    elif role != "branch supervisor":
        raise permission_exception

    for branch in current_user.branches:
        if branch.id == class_obj.branch_id:
            break
    else:
        raise permission_exception

    for student in class_obj.students:
        record = bulk_data.records.get(student.id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing student(s)"
            )

    existing_eval_query = select(Evaluation).where(
        and_(
            Evaluation.class_id == bulk_data.class_id,
            Evaluation.date == eval_date,
        )
    )
    existing_eval_result = await db.execute(existing_eval_query)
    existing_evals = existing_eval_result.scalars().all()
    existing_student_ids = {eval.student_id for eval in existing_evals}

    evaluations_to_create = []
    errors = []

    for student_id, eval_data in bulk_data.records.items():
        # Skip if evaluation already exists for this student/date
        if student_id in existing_student_ids:
            errors.append(
                f"Evaluation already exists for student {student_id} on {bulk_data.date}"
            )
            continue

        # Prepare evaluation grades
        evaluation_grades = [
            {"name": grade.name, "grade": grade.grade}
            for grade in eval_data.evaluations
        ]

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

    # 5. Bulk create evaluations
    if evaluations_to_create:
        db.add_all(evaluations_to_create)
        await db.commit()

        # Refresh to get the created objects with IDs
        for evaluation in evaluations_to_create:
            await db.refresh(evaluation)


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
