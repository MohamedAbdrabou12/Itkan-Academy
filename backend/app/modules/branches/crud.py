from typing import Any, Dict, List, Optional

from app.modules.branches.models import Branch, BranchStatus
from app.modules.branches.schemas import BranchCreate, BranchUpdate
from app.modules.classes.models import Class, ClassStatus
from app.modules.users.models import User, UserBranch
from fastapi import HTTPException, Request
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import and_, asc, desc, not_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class BranchCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ) -> Dict[str, Any]:
        query = select(Branch).options(
            selectinload(Branch.classes),
            selectinload(Branch.user_links).selectinload(UserBranch.user),
            selectinload(Branch.users_m2m),
        )

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Branch.name.ilike(search_term),
                    Branch.email.ilike(search_term),
                    Branch.phone.ilike(search_term),
                )
            )

        sort_columns = {
            "id": Branch.id,
            "name": Branch.name,
            "email": Branch.email,
            "phone": Branch.phone,
            "status": Branch.status,
            "created_at": Branch.created_at,
        }

        # Get sort column with fallback to id
        safe_sort_by = sort_by or "id"
        sort_column = sort_columns.get(safe_sort_by, Branch.id)

        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        result = await sqlalchemy_paginate(db, query)

        return result

    async def get_by_id(
        self, db: AsyncSession, branch_id: int, request: Optional[Request] = None
    ) -> Optional[Branch]:
        # Optional branch scoping
        if request:
            current_branch_id = getattr(request.state, "branch_id", None)
            if current_branch_id is not None and current_branch_id != branch_id:
                return None  # user cannot access other branches

        result = await db.execute(
            select(Branch)
            .where(Branch.id == branch_id)
            .options(
                selectinload(Branch.classes),
                selectinload(Branch.user_links).selectinload(UserBranch.user),
                selectinload(Branch.users_m2m),
            )
        )
        branch = result.scalars().first()
        if branch:
            # Calculate users count from the many-to-many relationship
            branch.users_count = len(branch.users_m2m)  # type: ignore
        return branch

    async def create(self, db: AsyncSession, branch_in: BranchCreate) -> Branch:
        branch = Branch(**branch_in.model_dump())
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch

    async def update(
        self, db: AsyncSession, branch_id: int, branch_in: BranchUpdate
    ) -> Branch:
        # Get the existing branch
        branch = await self.get_by_id(db, branch_id)
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        # Store old status to check if we're deactivating
        old_status = branch.status
        old_status_value = (
            old_status.value if isinstance(old_status, BranchStatus) else old_status
        )

        # Convert Pydantic model to dict, excluding unset fields
        update_data = branch_in.model_dump(exclude_unset=True)

        # Handle enum conversion
        if "status" in update_data and isinstance(update_data["status"], BranchStatus):
            update_data["status"] = update_data["status"].value

        # Update only the fields that were provided
        for field, value in update_data.items():
            setattr(branch, field, value)

        db.add(branch)
        await db.flush()  # Flush to get the updated branch status

        # Check if status changed from active to deactive
        new_status = update_data.get("status", old_status_value)
        if old_status_value == "active" and new_status == "deactive":
            await self.deactivate_related_entities(db, branch_id)

        await db.commit()
        await db.refresh(branch)
        return branch

    async def deactivate_related_entities(self, db: AsyncSession, branch_id: int):
        # Update users associated with this branch through user_branches
        # First get all user_ids associated with this branch
        user_branches_result = await db.execute(
            select(UserBranch.user_id).where(UserBranch.branch_id == branch_id)
        )
        user_ids = user_branches_result.scalars().all()

        if user_ids:
            # Update users status to deactive
            user_update_stmt = (
                update(User).where(User.id.in_(user_ids)).values(status="deactive")
            )
            await db.execute(user_update_stmt)

        # Update classes status to deactive
        class_update_stmt = (
            update(Class)
            .where(Class.branch_id == branch_id)
            .values(status=ClassStatus.deactive.value)
        )
        await db.execute(class_update_stmt)

    async def get_staff_by_branch(
        self,
        db: AsyncSession,
        branch_id: int,
        exclude_user_id: Optional[int] = None,
    ) -> List[User]:
        query = (
            select(User)
            .join(UserBranch)
            .where(
                and_(
                    not_(User.student.has()),
                    not_(User.parent.has()),
                )
            )
            .options(
                selectinload(User.role),
                selectinload(User.branch_links).joinedload(UserBranch.branch),
            )
        )

        if branch_id:
            query = query.where(UserBranch.branch_id == branch_id)

        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)

        query = query.order_by(User.full_name)

        result = await db.execute(query)
        return list(result.scalars().all())


branch_crud = BranchCRUD()
