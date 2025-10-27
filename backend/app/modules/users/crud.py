# app/modules/users/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.users import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: schemas.UserCreate):
    hashed_password = pwd_context.hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
