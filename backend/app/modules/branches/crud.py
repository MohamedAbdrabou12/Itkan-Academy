from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.branches import models, schemas


async def create_branch(db: AsyncSession, branch_in: schemas.BranchCreate):
    branch = models.Branch(**branch_in.dict())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch


async def get_branches(db: AsyncSession):
    result = await db.execute(select(models.Branch))
    return result.scalars().all()
