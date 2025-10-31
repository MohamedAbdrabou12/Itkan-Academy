from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class AuditLogBase(BaseModel):
    action: str
    user_id: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    meta: Optional[Dict] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
