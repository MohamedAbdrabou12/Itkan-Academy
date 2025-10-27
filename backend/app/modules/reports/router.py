from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.db.session import async_session
from app.modules.reports import crud, schemas

router = APIRouter()


# Correctly typed async generator for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@router.post("/")
async def generate_report(
    request: schemas.ReportRequest, db: AsyncSession = Depends(get_db)
):
    return await crud.generate_report(db, request.type)
