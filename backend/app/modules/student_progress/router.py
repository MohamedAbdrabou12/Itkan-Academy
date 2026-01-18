from typing import Annotated

from app.core.auth import get_current_user_id
from app.db.session import get_db
from app.modules.student_progress.crud import student_progress_crud
from app.modules.student_progress.schemas import (
    StudentProgressByStudentList,
    StudentProgressBySubjectList,
)
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

student_progress_router = APIRouter(prefix="/student-progress", tags=["Student Progress"])


@student_progress_router.get(
    "/as-student",
    status_code=status.HTTP_200_OK,
)
async def get_student_progress_as_student(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[User, Depends(get_current_user_id)],
) -> list[StudentProgressBySubjectList]:
    user = await student_progress_crud.get_user(db, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="لست مسجل الدخول")

    if user.student is not None:
        return await student_progress_crud.get_progress_student(
            db,
            user.student.id,
        )

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="لا يمكنك رؤية تقدم الطلاب")


@student_progress_router.get("/as-parent", status_code=status.HTTP_200_OK)
async def get_student_progress_as_parent(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[User, Depends(get_current_user_id)],
) -> list[StudentProgressByStudentList]:
    user = await student_progress_crud.get_user(db, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="لست مسجل الدخول")

    if user.parent is not None:
        return await student_progress_crud.get_progress_parent(
            db,
            [child.id for child in user.parent.children],
        )

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="لا يمكنك رؤية تقدم الطلاب")
