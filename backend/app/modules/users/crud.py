# backend/app/modules/users/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.users.models import User, UserStatus
from app.modules.users.schemas import UserCreate, UserUpdate

from app.core.security import get_password_hash as hash_password


class UserCRUD:
    async def get_all(self, db: AsyncSession) -> List[User]:
        result = await db.execute(
            select(User).options(
                selectinload(User.role),
                selectinload(User.branch),
            )
        )
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.role),
                selectinload(User.branch),
            )
        )
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(
            select(User)
            .where(User.email == email)
            .options(
                selectinload(User.role),
                selectinload(User.branch),
            )
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        hashed_password = hash_password(obj_in.password)
        db_obj = User(
            full_name=obj_in.full_name,
            email=obj_in.email,
            phone=obj_in.phone,
            password_hash=hashed_password,
            role_id=obj_in.role_id,
            branch_id=obj_in.branch_id,
            is_active=obj_in.is_active,
            mfa_enabled=obj_in.mfa_enabled,
            status=obj_in.status or UserStatus.pending,
        )
        db.add(db_obj)
        await db.flush()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
        data = obj_in.dict(exclude_unset=True)
        if "password" in data:
            data["password_hash"] = hash_password(data.pop("password"))
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, user_id: int) -> None:
        user = await self.get_by_id(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()


user_crud = UserCRUD()
