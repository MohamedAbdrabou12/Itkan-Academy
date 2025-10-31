from typing import List

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.audits.crud import audit_log_crud
from app.modules.audits.schemas import AuditLogCreate, AuditLogRead
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

audit_log_router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@audit_log_router.get(
    "/",
    response_model=List[AuditLogRead],
    dependencies=[Depends(get_current_user), Depends(require_permission("audit:view"))],
)
async def list_audit_logs(db: AsyncSession = Depends(get_db)):
    return await audit_log_crud.get_all(db)


@audit_log_router.get(
    "/{log_id}",
    response_model=AuditLogRead,
    dependencies=[Depends(get_current_user), Depends(require_permission("audit:view"))],
)
async def get_audit_log(log_id: int, db: AsyncSession = Depends(get_db)):
    log = await audit_log_crud.get_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


@audit_log_router.post(
    "/",
    response_model=AuditLogRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("audit:create")),
    ],
)
async def create_audit_log(log_in: AuditLogCreate, db: AsyncSession = Depends(get_db)):
    return await audit_log_crud.create(db, log_in)
