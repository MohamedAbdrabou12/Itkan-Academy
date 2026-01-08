from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.curriculums.crud.subject_unit import subject_unit_crud
from app.modules.curriculums.router.subject_unit_item import subject_unit_items_router
from app.modules.curriculums.schemas.subject_unit import (
    SubjectUnitCreate,
    SubjectUnitResponse,
    SubjectUnitUpdate,
)
from app.modules.curriculums.schemas.subject_unit_item import SubjectUnitItemResponse
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

subject_units_router = APIRouter(prefix="/units", tags=["Subject Units"])

subject_units_router.include_router(subject_unit_items_router)


@subject_units_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_CONTENT_ADD))],
)
async def create_subject_unit(
    db: Annotated[AsyncSession, Depends(get_db)], data: SubjectUnitCreate
) -> SubjectUnitResponse:
    subject_unit = await subject_unit_crud.create(db, data)
    return SubjectUnitResponse(
        id=subject_unit.id,
        title=subject_unit.title,
        description=subject_unit.description,
        subject_id=subject_unit.subject_id,
    )


@subject_units_router.get(
    "/{id}/items",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_CONTENT_VIEW))],
)
async def get_subject_unit_items(
    db: Annotated[AsyncSession, Depends(get_db)], id: int
) -> list[SubjectUnitItemResponse]:
    items = await subject_unit_crud.get_items(db, id)
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unit {id} not found")

    return [
        SubjectUnitItemResponse(
            id=item.id, title=item.title, type=item.type, content=item.content, unit_id=item.unit_id
        )
        for item in items
    ]


@subject_units_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_CONTENT_EDIT))],
)
async def edit_subject_unit(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, data: SubjectUnitUpdate
) -> None:
    await subject_unit_crud.update(db, id, data)
