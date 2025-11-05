from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.branches.schemas import BranchCreate, BranchRead, BranchUpdate
from app.modules.branches.crud import branch_crud

branch_router = APIRouter(prefix="/branches", tags=["Branches"])


@branch_router.get("/", response_model=List[BranchRead])
async def list_branches(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await branch_crud.get_all(db)


@branch_router.get("/{branch_id}", response_model=BranchRead)
async def get_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    branch = await branch_crud.get_by_id(db, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@branch_router.post(
    "/",
    response_model=BranchRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("branch:create")),
    ],
)
async def create_branch(branch_in: BranchCreate, db: AsyncSession = Depends(get_db)):
    return await branch_crud.create(db, branch_in)


@branch_router.put(
    "/{branch_id}",
    response_model=BranchRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("branch:update")),
    ],
)
async def update_branch(
    branch_id: int, branch_in: BranchUpdate, db: AsyncSession = Depends(get_db)
):
    branch = await branch_crud.get_by_id(db, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return await branch_crud.update(db, branch, branch_in)


@branch_router.delete(
    "/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("branch:delete")),
    ],
)
async def delete_branch(branch_id: int, db: AsyncSession = Depends(get_db)):
    await branch_crud.delete(db, branch_id)
    return None
