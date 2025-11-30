from typing import List, Optional
from app.core.security import get_password_hash as hash_password
from app.core.utils import create_password_reset_token
from app.modules.branches.models import Branch
from app.modules.users.models import User, UserBranch, UserStatus
from app.modules.users.schemas import BranchInfo, UserCreate, UserRead, UserUpdate
from app.services.notification_service.workrs.worker import send_notification_task
from fastapi import HTTPException, Request
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import asc, desc, or_
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


def map_user_to_read(user: User) -> UserRead:
    """
    Map User ORM object to UserRead schema including branches and permissions.
    """
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

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(User.full_name.ilike(search_term), User.email.ilike(search_term))
            )

        # Define sortable columns
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

        # Get sort column with fallback to id
        safe_sort_by = sort_by or "id"
        sort_column = sort_columns.get(safe_sort_by, User.id)

        # Apply sorting
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        result = await sqlalchemy_paginate(db, query)

        return result

    async def get_by_id(
        self, db: AsyncSession, user_id: int, request: Optional[Request] = None
    ) -> Optional[User]:
        """
        Get a single user by ID. Optionally filter by active branch.
        """
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.role),
                selectinload(User.teacher),
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
        """
        Get a user by email. No branch filtering.
        """
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
        """
        Sync user's many-to-many branches.
        """
        await db.execute(sa_delete(UserBranch).where(UserBranch.user_id == user.id))
        for bid in branch_ids:
            db.add(UserBranch(user_id=user.id, branch_id=bid))

        db.add(user)
        await db.commit()
        await db.refresh(user)

    async def create(
        self, db: AsyncSession, obj_in: dict | UserCreate
    ) -> Optional[User]:
        """
        Create a new user, sync branches, and send initial password reset email.
        """
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
        reset_link = f"http://localhost:5173/reset-password?token={token}"
        payload = {
            "username": db_obj.full_name,
            "reset_link": reset_link,
            "email": db_obj.email,
        }
        if db_obj and db_obj.email:
            send_notification_task.delay(
                user_id=db_obj.id,
                channel="email",
                template_type="reset_password",
                payload=payload,
            )
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: User, obj_in: dict | UserUpdate
    ) -> Optional[User]:
        """
        Update user fields and optionally sync branches.
        """
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

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        if branch_ids is not None:
            await self._sync_user_branches(db, db_obj, branch_ids)
            await db.refresh(db_obj)

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
        """
        Soft-delete user by setting status to deactive.
        """
        user = await self.get_by_id(db, user_id)
        if user:
            user.status = UserStatus.deactive.value
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    async def assign_branches(
        self, db: AsyncSession, user: User, branch_ids: List[int]
    ):
        """
        Assign multiple branches to user.
        """
        await self._sync_user_branches(db, user, branch_ids)
        return user


user_crud = UserCRUD()
