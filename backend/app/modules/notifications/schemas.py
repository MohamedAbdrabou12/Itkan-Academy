from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class NotificationBase(BaseModel):
    user_id: int
    channel: str  # e.g. "in_app", "email", "sms"
    template: Optional[str] = None
    payload: Optional[Dict] = None
    status: str = "pending"


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    status: Optional[str] = None
    sent_at: Optional[datetime] = None
    payload: Optional[Dict] = None


class NotificationRead(NotificationBase):
    id: int
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
