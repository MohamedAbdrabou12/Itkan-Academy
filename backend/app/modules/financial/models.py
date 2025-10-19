from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.db.base import Base
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # 'income' or 'expense'
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
