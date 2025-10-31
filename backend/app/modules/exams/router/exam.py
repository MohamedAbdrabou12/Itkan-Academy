from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.exams.schemas.exam import ExamCreate, ExamRead, ExamUpdate
from app.modules.exams.crud.exam import exam_crud

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get(
    "/",
    response_model=List[ExamRead],
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def list_exams(db: AsyncSession = Depends(get_db)):
    return await exam_crud.get_all(db)


@router.get(
    "/{exam_id}",
    response_model=ExamRead,
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    exam = await exam_crud.get_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.post(
    "/",
    response_model=ExamRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:create")),
    ],
)
async def create_exam(exam_in: ExamCreate, db: AsyncSession = Depends(get_db)):
    return await exam_crud.create(db, exam_in)


@router.put(
    "/{exam_id}",
    response_model=ExamRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:update")),
    ],
)
async def update_exam(
    exam_id: int, exam_in: ExamUpdate, db: AsyncSession = Depends(get_db)
):
    exam = await exam_crud.get_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return await exam_crud.update(db, exam, exam_in)


@router.delete(
    "/{exam_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:delete")),
    ],
)
async def delete_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    exam = await exam_crud.get_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    await exam_crud.delete(db, exam_id)
    return None
