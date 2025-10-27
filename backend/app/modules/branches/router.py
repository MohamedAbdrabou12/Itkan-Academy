from typing import AsyncGenerator
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.modules.branches import crud, schemas

router = APIRouter()


# Async generator for database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@router.post("/", response_model=schemas.BranchOut)
async def create_branch(
    branch_in: schemas.BranchCreate, db: AsyncSession = Depends(get_db)
):
    return await crud.create_branch(db, branch_in)


@router.get("/", response_model=list[schemas.BranchOut])
async def list_branches(db: AsyncSession = Depends(get_db)):
    return await crud.get_branches(db)
