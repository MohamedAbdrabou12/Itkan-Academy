# app/modules/permissions/schemas/permission.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None


class PermissionRead(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
