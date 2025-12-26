from typing import List, Optional

from app.core.security import get_password_hash as hash_password
from app.core.utils import create_password_reset_token
from app.modules.branches.models import Branch
from app.modules.role_permissions.models import RolePermission
from app.modules.roles.models import Role
from app.modules.users.models import User, UserBranch, UserStatus
from app.modules.users.schemas import BranchInfo, UserCreate, UserRead, UserUpdate
from app.services.notification_service.workrs.worker import send_notification_task
from fastapi import HTTPException, Request
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import and_, asc, desc, not_, or_
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload


def map_user_to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id,
        role_name=user.role_name,
        role_name_ar=user.role_name_ar,
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
        login_identifier=user.login_identifier,
        login_type=user.login_type,
    )


class UserCRUD:
    async def get_all_staff(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ):
        query = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.branch_links).joinedload(UserBranch.branch),
            )
            .where(
                and_(
                    not_(User.teacher.has()),
                    not_(User.student.has()),
                    not_(User.parent.has()),
                )
            )
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

        sort_column = sort_columns.get(sort_by, User.id)
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        result = await paginate(db, query)
        return result

    async def get_by_id(
        self, db: AsyncSession, user_id: int, request: Optional[Request] = None
    ) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.role).options(
                    selectinload(Role.permission_associations).selectinload(
                        RolePermission.permission
                    )
                ),
                selectinload(User.teacher),
                selectinload(User.branch_links).joinedload(UserBranch.branch),
                selectinload(User.branches),
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

    async def get_by_login_identifier(
        self, db: AsyncSession, identifier: str
    ) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.login_identifier == identifier)
            .options(
                selectinload(User.role)
                .selectinload(Role.permission_associations)
                .selectinload(RolePermission.permission),
                selectinload(User.branch_links).joinedload(UserBranch.branch),
                selectinload(User.branches),
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def _sync_user_branches(
        self, db: AsyncSession, user: User, branch_ids: List[int]
    ):
        await db.execute(sa_delete(UserBranch).where(UserBranch.user_id == user.id))
        for bid in branch_ids:
            db.add(UserBranch(user_id=user.id, branch_id=bid))
        db.add(user)
        await db.commit()
        await db.refresh(user)

    async def create(
        self, db: AsyncSession, obj_in: dict | UserCreate, is_staff: bool = False
    ) -> Optional[User]:
        data = (
            obj_in.dict(exclude_unset=True)
            if not isinstance(obj_in, dict)
            else obj_in.copy()
        )
        # if "password" in data:
        #     data["password_hash"] = hash_password(data.pop("password"))
        password = data.pop("password", None)
        if password:
            data["password_hash"] = hash_password(password)
        else:
            data["password_hash"] = ""

        status_val = data.get("status", UserStatus.pending.value)
        if isinstance(status_val, UserStatus):
            status_val = status_val.value

        db_obj = User(
            full_name=data["full_name"],
            email=data.get("email"),
            phone=data.get("phone"),
            password_hash=data.get("password_hash", ""),
            role_id=data.get("role_id"),
            status=status_val,
            login_identifier=data.get("email")
            if is_staff
            else data["login_identifier"],
            login_type="email" if is_staff else data["login_type"],
        )
        db.add(db_obj)
        await db.commit()

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
            await db.commit()

        token = create_password_reset_token(db_obj.id)
        reset_link = f"http://localhost:5173/reset-password?token={token}"
        if db_obj.email:
            send_notification_task.delay(
                user_id=db_obj.id,
                channel="email",
                template_type="reset_password",
                payload={
                    "username": db_obj.full_name,
                    "reset_link": reset_link,
                    "email": db_obj.email,
                },
            )

        stmt = (
            select(User)
            .where(User.id == db_obj.id)
            .options(joinedload(User.role), selectinload(User.branches))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

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
        await self._sync_user_branches(db, user, branch_ids)
        return user


user_crud = UserCRUD()
