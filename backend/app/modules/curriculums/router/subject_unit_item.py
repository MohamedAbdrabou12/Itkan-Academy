from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.curriculums.crud.subject_unit_item import subject_unit_item_crud
from app.modules.curriculums.schemas.subject_unit_item import (
    SubjectUnitItemCreate,
    SubjectUnitItemResponse,
    SubjectUnitItemUpdate,
)
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

subject_unit_items_router = APIRouter(prefix="/items", tags=["Subject Unit Items"])


@subject_unit_items_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_CONTENT_EDIT))],
)
async def create_subject_unit_item(
    db: Annotated[AsyncSession, Depends(get_db)], data: SubjectUnitItemCreate
) -> SubjectUnitItemResponse:
    item = await subject_unit_item_crud.create(db, data)
    return SubjectUnitItemResponse(
        id=item.id, title=item.title, type=item.type, content=item.content, unit_id=item.unit_id
    )


@subject_unit_items_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_CONTENT_EDIT))],
)
async def edit_subject_unit_item(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, data: SubjectUnitItemUpdate
) -> None:
    await subject_unit_item_crud.update(db, id, data)
