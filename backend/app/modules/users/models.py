# app/modules/users/models.py
from sqlalchemy import String, Boolean, Column
from app.db.base import Base
from sqlalchemy import Integer


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String(512), nullable=False)
