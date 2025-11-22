from typing import List, Optional
from app.core.security import get_password_hash as hash_password
from app.core.utils import create_password_reset_token
from app.modules.branches.models import Branch
from app.modules.users.models import User, UserBranch, UserStatus
from app.modules.users.schemas import BranchInfo, UserCreate, UserRead, UserUpdate
from app.services.notification_service.tasks.email import send_email_task
from app.services.notification_service.utils.template_engine import render_template
from fastapi import HTTPException, Request
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import asc, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


def map_user_to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id,
        role_name=user.role_name,
        role_name_ar=user.role_name_ar,
        branch_name=user.branch_name,
        status=user.status,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
        branch_ids=[link.branch_id for link in user.branch_links]
        if user.branch_links
        else None,
        branches=[BranchInfo.from_orm(link.branch) for link in user.branch_links]
        if user.branch_links
        else None,
    )


class UserCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ):
        query = select(User).options(
            selectinload(User.role),
            selectinload(User.branch_links).joinedload(UserBranch.branch),
        )
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(User.full_name.ilike(search_term), User.email.ilike(search_term))
            )
        sort_columns = {
            "id": User.id,
            "full_name": User.full_name,
            "email": User.email,
            "phone": User.phone,
            "role_name": User.role_name,
            "status": User.status,
            "last_login": User.last_login,
            "created_at": User.created_at,
            "updated_at": User.updated_at,
        }
        sort_column = sort_columns.get(sort_by or "id", User.id)
        query = query.order_by(
            desc(sort_column)
            if sort_order and sort_order.lower() == "desc"
            else asc(sort_column)
        )
        return await sqlalchemy_paginate(db, query)

    async def get_by_id(
        self, db: AsyncSession, user_id: int, request: Optional[Request] = None
    ) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.role),
                selectinload(User.branch_links).joinedload(UserBranch.branch),
            )
        )
        if request:
            active_branch = getattr(request.state, "active_branch_id", None)
            if active_branch is not None:
                stmt = stmt.join(User.branch_links).where(
                    UserBranch.branch_id == active_branch
                )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.email == email)
            .options(
                selectinload(User.role),
                selectinload(User.branch_links).joinedload(UserBranch.branch),
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def _sync_user_branches(
        self, db: AsyncSession, user: User, branch_ids: List[int]
    ):
        user.branch_links.clear()
        await db.flush()
        for bid in branch_ids:
            user.branch_links.append(UserBranch(user_id=user.id, branch_id=bid))
        await db.commit()
        await db.refresh(user)

    async def create(
        self, db: AsyncSession, obj_in: dict | UserCreate
    ) -> Optional[User]:
        data = (
            obj_in.dict(exclude_unset=True)
            if not isinstance(obj_in, dict)
            else obj_in.copy()
        )
        if "password" in data:
            data["password_hash"] = hash_password(data.pop("password"))
        status_val = data.get("status", UserStatus.pending.value)
        if isinstance(status_val, UserStatus):
            status_val = status_val.value
        db_obj = User(
            full_name=data["full_name"],
            email=data["email"],
            phone=data.get("phone"),
            password_hash=data.get("password_hash", ""),
            role_id=data.get("role_id"),
            status=status_val,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        branch_ids = data.get("branch_ids")
        if branch_ids:
            result = await db.execute(
                select(Branch.id).where(Branch.id.in_(branch_ids))
            )
            existing_ids = [row[0] for row in result.fetchall()]
            missing = set(branch_ids) - set(existing_ids)
            if missing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid or missing branch_ids: {', '.join(map(str, missing))}",
                )
            await self._sync_user_branches(db, db_obj, branch_ids)
        token = create_password_reset_token(db_obj.id)
        reset_link = f"https://www.google.com/search?q={token}"
        subject, body_html = render_template(
            "reset_password.html",
            {"username": db_obj.full_name, "reset_link": reset_link},
        )
        send_email_task.delay(db_obj.email, subject, body_html)
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: User, obj_in: dict | UserUpdate
    ) -> Optional[User]:
        data = (
            obj_in.dict(exclude_unset=True)
            if not isinstance(obj_in, dict)
            else obj_in.copy()
        )
        if "password" in data:
            data["password_hash"] = hash_password(data.pop("password"))
        if "status" in data and isinstance(data["status"], UserStatus):
            data["status"] = data["status"].value
        branch_ids = data.pop("branch_ids", None)
        for field, value in data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        if branch_ids is not None:
            await self._sync_user_branches(db, db_obj, branch_ids)
        return db_obj

    async def update_role(
        self, db: AsyncSession, user: User, role_id: int
    ) -> Optional[User]:
        try:
            user.role_id = role_id
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise e

    async def delete(self, db: AsyncSession, user_id: int) -> Optional[User]:
        user = await self.get_by_id(db, user_id)
        if user:
            user.status = UserStatus.deactive.value
            await db.commit()
            await db.refresh(user)
        return user

    async def assign_branches(
        self, db: AsyncSession, user: User, branch_ids: List[int]
    ):
        await self._sync_user_branches(db, user, branch_ids)
        return user


user_crud = UserCRUD()
