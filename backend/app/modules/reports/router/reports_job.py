from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.db.session import async_session
from backend.app.modules.reports.crud import reports_job
from backend.app.modules.reports.schema.reports_job import (
    reports_job as reports_job_schema,  # noqa F401
)

router = APIRouter()


# Correctly typed async generator for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@router.post("/")
async def generate_report(
    request: reports_job.ReportRequest, db: AsyncSession = Depends(get_db)
):
    return await reports_job.generate_report(db, request.type)
