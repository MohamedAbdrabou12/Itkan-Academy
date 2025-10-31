from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.reports.schemas.report_job import (
    ReportJobCreate,
    ReportJobRead,
    ReportJobUpdate,
)
from app.modules.reports.crud.report_job import report_job_crud

router = APIRouter(prefix="/report-jobs", tags=["Report Jobs"])


@router.get(
    "/",
    response_model=List[ReportJobRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("report:view")),
    ],
)
async def list_report_jobs(db: AsyncSession = Depends(get_db)):
    return await report_job_crud.get_all(db)


@router.get(
    "/{job_id}",
    response_model=ReportJobRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("report:view")),
    ],
)
async def get_report_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await report_job_crud.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Report job not found")
    return job


@router.post(
    "/",
    response_model=ReportJobRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("report:create")),
    ],
)
async def create_report_job(
    job_in: ReportJobCreate, db: AsyncSession = Depends(get_db)
):
    return await report_job_crud.create(db, job_in)


@router.put(
    "/{job_id}",
    response_model=ReportJobRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("report:update")),
    ],
)
async def update_report_job(
    job_id: int, job_in: ReportJobUpdate, db: AsyncSession = Depends(get_db)
):
    job = await report_job_crud.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Report job not found")
    return await report_job_crud.update(db, job, job_in)


@router.put(
    "/{job_id}/mark-completed",
    response_model=ReportJobRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("report:update")),
    ],
)
async def mark_completed(
    job_id: int, result_url: str, db: AsyncSession = Depends(get_db)
):
    job = await report_job_crud.mark_completed(db, job_id, result_url)
    if not job:
        raise HTTPException(status_code=404, detail="Report job not found")
    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("report:delete")),
    ],
)
async def delete_report_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await report_job_crud.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Report job not found")
    await db.delete(job)
    await db.commit()
    return None
