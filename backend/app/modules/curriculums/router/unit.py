from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.curriculums.crud.unit import unit_crud
from app.modules.curriculums.router.unit_item import unit_items_router
from app.modules.curriculums.schemas.unit import (
    UnitCreate,
    UnitResponse,
    UnitUpdate,
)
from app.modules.curriculums.schemas.unit_item import UnitItemResponse
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

units_router = APIRouter(prefix="/units", tags=["Subject Units"])

units_router.include_router(unit_items_router)


@units_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_ADD))],
)
async def create_unit(
    db: Annotated[AsyncSession, Depends(get_db)], data: UnitCreate
) -> UnitResponse:
    unit = await unit_crud.create(db, data)
    return UnitResponse(
        id=unit.id,
        title=unit.title,
        description=unit.description,
        subject_id=unit.subject_id,
    )


@units_router.get(
    "/{id}/items",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_VIEW))],
)
async def get_unit_items(
    db: Annotated[AsyncSession, Depends(get_db)], id: int
) -> list[UnitItemResponse]:
    items = await unit_crud.get_items(db, id)
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unit {id} not found")

    return [
        UnitItemResponse(
            id=item.id, title=item.title, type=item.type, content=item.content, unit_id=item.unit_id
        )
        for item in items
    ]


@units_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_EDIT))],
)
async def edit_unit(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, data: UnitUpdate
) -> None:
    await unit_crud.update(db, id, data)
