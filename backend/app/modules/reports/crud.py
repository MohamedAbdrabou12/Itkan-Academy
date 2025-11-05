from datetime import datetime
from typing import List, Optional

from app.modules.reports.models import ReportJob
from app.modules.reports.schemas import ReportJobCreate, ReportJobUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ReportJobCRUD:
    async def get_all(self, db: AsyncSession) -> List[ReportJob]:
        result = await db.execute(
            select(ReportJob).order_by(ReportJob.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, job_id: int) -> Optional[ReportJob]:
        return await db.get(ReportJob, job_id)

    async def create(self, db: AsyncSession, job_in: ReportJobCreate) -> ReportJob:
        job = ReportJob(**job_in.dict())
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    async def update(
        self, db: AsyncSession, job: ReportJob, job_in: ReportJobUpdate
    ) -> ReportJob:
        for field, value in job_in.dict(exclude_unset=True).items():
            setattr(job, field, value)
        job.updated_at = datetime.utcnow()
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    async def mark_in_progress(
        self, db: AsyncSession, job_id: int
    ) -> Optional[ReportJob]:
        job = await self.get_by_id(db, job_id)
        if job:
            job.status = "in_progress"
            job.updated_at = datetime.utcnow()
            db.add(job)
            await db.commit()
            await db.refresh(job)
        return job

    async def mark_completed(
        self, db: AsyncSession, job_id: int, result_url: str
    ) -> Optional[ReportJob]:
        job = await self.get_by_id(db, job_id)
        if job:
            job.status = "completed"
            job.result_url = result_url
            job.updated_at = datetime.utcnow()
            db.add(job)
            await db.commit()
            await db.refresh(job)
        return job

    async def mark_failed(self, db: AsyncSession, job_id: int) -> Optional[ReportJob]:
        job = await self.get_by_id(db, job_id)
        if job:
            job.status = "failed"
            job.updated_at = datetime.utcnow()
            db.add(job)
            await db.commit()
            await db.refresh(job)
        return job


report_job_crud = ReportJobCRUD()
