from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.modules.audits.models.audit_log import AuditLog
from app.modules.audits.schemas.audit_log import AuditLogCreate


class AuditLogCRUD:
    async def get_all(self, db: AsyncSession) -> List[AuditLog]:
        result = await db.execute(
            AuditLog.__table__.select().order_by(AuditLog.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, log_id: int) -> Optional[AuditLog]:
        result = await db.get(AuditLog, log_id)
        return result

    async def create(self, db: AsyncSession, log_in: AuditLogCreate) -> AuditLog:
        log = AuditLog(**log_in.dict())
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log


audit_log_crud = AuditLogCRUD()
