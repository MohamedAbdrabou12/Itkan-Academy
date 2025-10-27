from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.financial import models, schemas
from datetime import datetime


async def create_transaction(db: AsyncSession, txn_in: schemas.TransactionCreate):
    txn = models.Transaction(**txn_in.dict(), created_at=datetime.utcnow())
    db.add(txn)
    await db.commit()
    await db.refresh(txn)
    return txn


async def get_transactions(db: AsyncSession):
    result = await db.execute(select(models.Transaction))
    return result.scalars().all()
