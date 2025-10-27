from sqlalchemy import String, Boolean, Column, Integer
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    full_name: str | None = Column(String(255), nullable=True)
    is_active: bool = Column(Boolean, default=True)
    hashed_password: str = Column(String(512), nullable=False)
