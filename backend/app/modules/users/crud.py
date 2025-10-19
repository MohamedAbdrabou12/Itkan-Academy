# app/modules/users/crud.py
from sqlalchemy.orm import Session
from app.modules.users import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate):
    fake_hashed = pwd_context.hash(user_in.password)
    db_user = models.User(
        email=user_in.email, full_name=user_in.full_name, hashed_password=fake_hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
