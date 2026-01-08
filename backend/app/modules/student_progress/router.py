from typing import Annotated

from app.core.auth import get_current_user_id
from app.db.session import get_db
from app.modules.student_progress.crud import student_progress_crud
from app.modules.student_progress.schemas import StudentProgressResponse
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

student_progress_router = APIRouter(prefix="/student-progress", tags=["Student Progress"])


@student_progress_router.get(
    "/as-student/{subject_id}",
    status_code=status.HTTP_200_OK,
)
async def get_student_progress(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[User, Depends(get_current_user_id)],
    subject_id: int,
) -> list[StudentProgressResponse]:
    user = (
        await db.execute(select(User).where(User.id == user_id).options(selectinload(User.student)))
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not logged in")

    if user.student is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to see student progress"
        )

    progress = await student_progress_crud.student_get_progress(db, user.student.id, subject_id)
    return [
        StudentProgressResponse(
            id=item.id,
            student_id=item.student_id,
            unit_item_id=item.unit_item_id,
            evaluation_id=getattr(item, "evaluation_id", None),
            exam_attempt_id=getattr(item, "exam_attempt_id", None),
            created_at=item.created_at,
        )
        for item in progress
    ]


@student_progress_router.get("/as-parent/{subject_id}", status_code=status.HTTP_200_OK)
async def get_parent_children_progress(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[User, Depends(get_current_user_id)],
    subject_id: int,
) -> None:
    user = (
        await db.execute(select(User).where(User.id == user_id).options(selectinload(User.parent)))
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not logged in")

    if user.parent is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to see student progress"
        )

    progress = await student_progress_crud.parent_get_progress(
        db, (child.id for child in user.parent.children), subject_id
    )

    return [
        StudentProgressResponse(
            id=item.id,
            student_id=item.student_id,
            unit_item_id=item.unit_item_id,
            evaluation_id=getattr(item, "evaluation_id", None),
            exam_attempt_id=getattr(item, "exam_attempt_id", None),
            created_at=item.created_at,
        )
        for item in progress
    ]
