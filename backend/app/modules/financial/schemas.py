from pydantic import BaseModel
from datetime import datetime


class TransactionCreate(BaseModel):
    type: str
    amount: float
    description: str | None = None
    created_by: int


class TransactionOut(BaseModel):
    id: int
    type: str
    amount: float
    description: str | None
    created_at: datetime
    created_by: int

    class Config:
        orm_mode = True
