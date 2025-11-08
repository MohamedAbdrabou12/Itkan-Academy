from typing import Any, Dict, Optional

from app.modules.branches.models import Branch, BranchStatus
from app.modules.branches.schemas import BranchCreate, BranchUpdate
from app.modules.classes.models import Class, ClassStatus
from app.modules.users.models import User
from fastapi import HTTPException, Request
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import asc, desc, or_, update
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
        query = select(Branch).options(selectinload(Branch.users))

        # Apply search filter
        if search:
            search_filter = or_(
                Branch.name.ilike(f"%{search}%"),
                Branch.email.ilike(f"%{search}%"),
                Branch.phone.ilike(f"%{search}%"),
                Branch.address.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

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
            .options(selectinload(Branch.users))
        )
        branch = result.scalars().first()
        if branch:
            branch.users_count = len(branch.users)  # type: ignore
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
        # Update users status to deactive
        user_update_stmt = (
            update(User)
            .where(User.branch_id == branch_id)
            .values(status=BranchStatus.deactive.value)
        )
        await db.execute(user_update_stmt)

        # Update classes status to deactive
        class_update_stmt = (
            update(Class)
            .where(Class.branch_id == branch_id)
            .values(status=ClassStatus.deactive.value)
        )
        await db.execute(class_update_stmt)


branch_crud = BranchCRUD()
