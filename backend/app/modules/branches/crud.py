# backend/app/modules/branches/crud.py
from typing import List, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.branches.models import Branch
from app.modules.branches.schemas import BranchCreate, BranchUpdate


class BranchCRUD:
    async def get_all(
        self, db: AsyncSession, request: Optional[Request] = None
    ) -> List[Branch]:
        query = select(Branch).options(selectinload(Branch.users)).order_by(Branch.id)

        # Branch scoping placeholder
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                query = query.where(Branch.id == branch_id)

        result = await db.execute(query)
        branches = result.scalars().all()
        for b in branches:
            b.users_count = len(b.users)
        return branches

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
            branch.users_count = len(branch.users)
        return branch

    async def create(self, db: AsyncSession, branch_in: BranchCreate) -> Branch:
        branch = Branch(**branch_in.dict())
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch

    async def update(
        self, db: AsyncSession, branch: Branch, branch_in: BranchUpdate
    ) -> Branch:
        data = branch_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(branch, field, value)
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch

    async def delete(self, db: AsyncSession, branch_id: int) -> None:
        branch = await self.get_by_id(db, branch_id)
        if branch:
            await db.delete(branch)
            await db.commit()


branch_crud = BranchCRUD()
