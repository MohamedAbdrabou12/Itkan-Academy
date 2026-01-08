from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.curriculums.crud.unit_item import unit_item_crud
from app.modules.curriculums.schemas.unit_item import (
    UnitItemCreate,
    UnitItemResponse,
    UnitItemUpdate,
)
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

unit_items_router = APIRouter(prefix="/items", tags=["Subject Unit Items"])


@unit_items_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_EDIT))],
)
async def create_unit_item(
    db: Annotated[AsyncSession, Depends(get_db)], data: UnitItemCreate
) -> UnitItemResponse:
    item = await unit_item_crud.create(db, data)
    return UnitItemResponse(
        id=item.id, title=item.title, type=item.type, content=item.content, unit_id=item.unit_id
    )


@unit_items_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_EDIT))],
)
async def edit_unit_item(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, data: UnitItemUpdate
) -> None:
    await unit_item_crud.update(db, id, data)
