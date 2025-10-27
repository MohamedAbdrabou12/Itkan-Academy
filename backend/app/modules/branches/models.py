from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Branch(Base):
    __tablename__ = "branches"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(255), unique=True, nullable=False)
    address: str | None = Column(String(255), nullable=True)
    phone: str | None = Column(String(50), nullable=True)
