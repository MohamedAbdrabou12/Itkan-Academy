from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class PaymentBase(BaseModel):
    invoice_id: int
    external_txn_id: Optional[str] = None
    gateway: Optional[str] = None  # e.g., "stripe", "paypal", "wallet"
    amount: Optional[float] = None
    status: str = "pending"
    paid_at: Optional[datetime] = None
    inf_metadata: Optional[Dict] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    external_txn_id: Optional[str] = None
    gateway: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    paid_at: Optional[datetime] = None
    inf_metadata: Optional[Dict] = None


class PaymentRead(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
