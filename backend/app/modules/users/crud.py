# backend/app/modules/users/crud.py
# # ==========================================================================================
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import Request
from app.core.security import get_password_hash as hash_password
from app.modules.users.models import User, UserStatus
from app.modules.users.schemas import UserCreate, UserUpdate
from app.core.utils import create_password_reset_token
from app.core.config import settings  # noqa
from app.services.notification_service.tasks.email import send_email_task
from app.services.notification_service.utils.template_engine import render_template


class UserCRUD:
    async def get_all(
        self, db: AsyncSession, request: Optional[Request] = None
    ) -> List[User]:
        stmt = select(User).options(selectinload(User.role), selectinload(User.branch))

        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = stmt.where(User.branch_id == branch_id)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, user_id: int, request: Optional[Request] = None
    ) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.role), selectinload(User.branch))
        )

        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = stmt.where(User.branch_id == branch_id)

        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.role), selectinload(User.branch))
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: dict | UserCreate) -> User:
        # دعم dict أو Pydantic object
        data = (
            obj_in.dict(exclude_unset=True)
            if not isinstance(obj_in, dict)
            else obj_in.copy()
        )

        hashed_password = data.get("password_hash", "")
        status = data.get("status", UserStatus.pending)
        if isinstance(status, UserStatus):
            status = status.value  # تحويل Enum لـ str

        db_obj = User(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
            password_hash=hashed_password,
            role_id=data.get("role_id"),
            branch_id=data.get("branch_id"),
            status=status,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Generate reset password token
        token = create_password_reset_token(db_obj.id)
        reset_link = f"https://www.google.com/search?q={token}"  # Temporary for testing

        # Render email using template
        subject, body_html = render_template(
            "reset_password.html",
            {"username": db_obj.name, "reset_link": reset_link},
        )
        send_email_task.delay(db_obj.email, subject, body_html)

        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: User, obj_in: dict | UserUpdate
    ) -> User:
        data = (
            obj_in.dict(exclude_unset=True) if not isinstance(obj_in, dict) else obj_in
        )

        if "password" in data:
            data["password_hash"] = hash_password(data.pop("password"))

        if "status" in data and isinstance(data["status"], UserStatus):
            data["status"] = data["status"].value

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