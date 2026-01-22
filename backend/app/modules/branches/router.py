from typing import Annotated, Optional

from app.core.auth import get_current_user_id
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.branches.crud import branch_crud
from app.modules.branches.schemas import (
    BranchCreate,
    BranchRead,
    BranchUpdate,
)
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

branch_router = APIRouter(prefix="/branches", tags=["Branches"])


@branch_router.get(
    "/",
    response_model=Page[BranchRead],
)
async def list_branches(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
):
    return await branch_crud.get_all(
        db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@branch_router.get("/me")
async def get_current_user_branches(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> list[BranchRead]:
    return [
        BranchRead(
            id=branch.id,
            name=branch.name,
            email=branch.email,
            phone=branch.phone,
            address=branch.address,
            status=branch.status,
            created_at=branch.created_at,
        )
        for branch in await branch_crud.get_user_branches(db, user_id)
    ]


# @branch_router.get(
#     "/{branch_id}",
#     response_model=BranchRead,
#     dependencies=[
#         Depends(get_current_user),
#         Depends(require_permission("branch:view")),
#     ],
# )
# async def get_branch(
#     branch_id: int, request: Request, db: AsyncSession = Depends(get_db)
# ):
#     branch = await branch_crud.get_by_id(db, branch_id, request=request)
#     if not branch:
#         raise HTTPException(status_code=404, detail="Branch not found")
#     return branch


@branch_router.post(
    "/",
    response_model=BranchRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.SYSTEM_BRANCHES_ADD))],
)
async def create_branch(
    branch_in: BranchCreate,
    db: AsyncSession = Depends(get_db),
):
    return await branch_crud.create(db, branch_in)


@branch_router.put(
    "/{branch_id}",
    response_model=BranchRead,
    dependencies=[Depends(require_permission(PermissionCode.SYSTEM_BRANCHES_EDIT))],
)
async def update_branch(
    branch_id: int,
    branch_in: BranchUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await branch_crud.update(db, branch_id, branch_in)
