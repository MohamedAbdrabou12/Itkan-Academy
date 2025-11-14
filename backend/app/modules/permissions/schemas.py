
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    code: str
    name: str
    name_ar: str
    description: Optional[str] = None
    description_ar: Optional[str] = None


class Permission(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
