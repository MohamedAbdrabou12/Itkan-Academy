from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class InvoiceBase(BaseModel):
    student_id: int
    amount: float
    due_date: date
    status: str = "unpaid"
    description: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    amount: Optional[float] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None


class InvoiceRead(InvoiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
