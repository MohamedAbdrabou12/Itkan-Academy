from typing import Optional

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.branches.crud import branch_crud
from app.modules.branches.schemas import (
    BranchCreate,
    BranchRead,
    BranchUpdate,
    BranchesResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

branch_router = APIRouter(prefix="/branches", tags=["Branches"])


@branch_router.get(
    "/",
    response_model=BranchesResponse,
    dependencies=[
        # Depends(get_current_user),
        # Depends(require_permission("branch:view")),
    ],
)
async def list_branches(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
):
    return await branch_crud.get_all(
        db,
        request=request,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@branch_router.get(
    "/{branch_id}",
    response_model=BranchRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("branch:view")),
    ],
)
async def get_branch(
    branch_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    branch = await branch_crud.get_by_id(db, branch_id, request=request)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@branch_router.post(
    "/",
    response_model=BranchRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        # Depends(get_current_user),
        # Depends(require_permission("branch:create")),
    ],
)
async def create_branch(branch_in: BranchCreate, db: AsyncSession = Depends(get_db)):
    return await branch_crud.create(db, branch_in)


@branch_router.put(
    "/{branch_id}",
    response_model=BranchRead,
    dependencies=[
        # Depends(get_current_user),
        # Depends(require_permission("branch:update")),
    ],
)
async def update_branch(
    branch_id: int, branch_in: BranchUpdate, db: AsyncSession = Depends(get_db)
):
    return await branch_crud.update(db, branch_id, branch_in)


@branch_router.delete(
    "/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        # Depends(get_current_user),
        # Depends(require_permission("branch:delete")),
    ],
)
async def delete_branch(branch_id: int, db: AsyncSession = Depends(get_db)):
    await branch_crud.delete(db, branch_id)
    return None
