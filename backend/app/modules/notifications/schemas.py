from pydantic import BaseModel, Json
from typing import Literal
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


class NotificationBase(BaseModel):
    user_id: str
    channel: str
    template: str
    payload: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: uuid.UUID
    status: str
    failed_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True


class NotificationRequest(BaseModel):
    user_id: int
    channel: Literal["email", "web"]
    template_type: str
    payload: dict
