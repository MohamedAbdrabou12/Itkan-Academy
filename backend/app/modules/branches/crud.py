from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.modules.branches.models import Branch
from app.modules.branches.schemas import BranchCreate, BranchUpdate


class BranchCRUD:
    async def get_all(self, db: AsyncSession) -> List[Branch]:
        result = await db.execute(Branch.__table__.select().order_by(Branch.id))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, branch_id: int) -> Optional[Branch]:
        result = await db.get(Branch, branch_id)
        return result

    async def create(self, db: AsyncSession, branch_in: BranchCreate) -> Branch:
        branch = Branch(**branch_in.dict())
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch

    async def update(
        self, db: AsyncSession, branch: Branch, branch_in: BranchUpdate
    ) -> Branch:
        for field, value in branch_in.dict(exclude_unset=True).items():
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
