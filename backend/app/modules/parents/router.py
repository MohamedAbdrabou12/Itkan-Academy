from typing import Optional
from fastapi import APIRouter, Depends, Request, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.parents.schemas import ParentCreate, ParentRead, ParentUpdate
from app.modules.parents.service import ParentService
from app.modules.users.models import User

parents_router = APIRouter(prefix="/parents", tags=["Parents"])


@parents_router.get(
    "/",
    response_model=dict,
    dependencies=[Depends(require_permission("parent.management.view"))],
)
async def list_parents(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
):
    return await ParentService.list_parents(
        db, page=page, size=size, search=search, sort_by=sort_by, sort_order=sort_order
    )


@parents_router.get(
    "/{parent_id}",
    response_model=ParentRead,
    dependencies=[Depends(require_permission("parent.management.view"))],
)
async def get_parent(parent_id: int, db: AsyncSession = Depends(get_db)):
    return await ParentService.get_parent(db, parent_id)


@parents_router.post(
    "/",
    response_model=ParentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("parent.management.add"))],
)
async def create_parent(
    parent_in: ParentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = parent_in.model_dump()
    return await ParentService.create_parent(db, payload, creator=current_user)


@parents_router.put(
    "/{parent_id}",
    response_model=ParentRead,
    dependencies=[Depends(require_permission("parent.management.edit"))],
)
async def update_parent(
    parent_id: int,
    parent_in: ParentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = parent_in.model_dump(exclude_unset=True)
    return await ParentService.update_parent(db, parent_id, data)


@parents_router.delete(
    "/{parent_id}",
    response_model=ParentRead,
    dependencies=[Depends(require_permission("parent.management.delete"))],
)
async def delete_parent(
    parent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ParentService.delete_parent(db, parent_id)


@parents_router.post(
    "/{parent_id}/children/{student_id}",
    response_model=ParentRead,
    dependencies=[Depends(require_permission("parent.link_child"))],
)
async def link_child(
    request: Request,
    parent_id: int,
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ParentService.link_child(db, parent_id, student_id, request=request)


@parents_router.delete(
    "/{parent_id}/children/{student_id}",
    response_model=ParentRead,
    dependencies=[Depends(require_permission("parent.unlink_child"))],
)
async def unlink_child(
    parent_id: int,
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ParentService.unlink_child(db, parent_id, student_id)
