from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    address = Column(String(255))
    phone = Column(String(50))
