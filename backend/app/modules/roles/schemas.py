from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleRead(BaseModel):
    id: int
    name: str
    description: str
    name_in_arabic: str
    created_at: datetime
    # updated_at: datetime
    # permissions: List[PermissionRead] = []

    class Config:
        from_attributes = True
