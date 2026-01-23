from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.curriculums.crud.curriculum import curriculum_crud
from app.modules.curriculums.schemas.curriculum import (
    CurriculumCreate,
    CurriculumResponse,
    CurriculumUpdate,
)
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

curriculums_router = APIRouter(prefix="/curriculums", tags=["Curriculums"])


@curriculums_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_ADD))],
)
async def create_curriculum(
    data: CurriculumCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CurriculumResponse:
    curriculum = await curriculum_crud.create(db, data)
    return CurriculumResponse(
        id=curriculum.id,
        name=curriculum.name,
        description=curriculum.description,
        academic_year=curriculum.academic_year,
        is_active=curriculum.is_active,
    )


@curriculums_router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_curriculums(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str | None, Query()] = "id",
    sort_order: Annotated[str | None, Query()] = "asc",
) -> Page[CurriculumResponse]:
    return await curriculum_crud.get_all(db, search, sort_by, sort_order)


@curriculums_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_EDIT))],
)
async def edit_curriculum(
    id: int,
    data: CurriculumUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await curriculum_crud.update(db, id, data)
