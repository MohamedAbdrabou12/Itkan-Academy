from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.modules.financial.models.payment import Payment
from app.modules.financial.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentCRUD:
    async def get_all(self, db: AsyncSession) -> List[Payment]:
        result = await db.execute(select(Payment).order_by(Payment.created_at.desc()))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, payment_id: int) -> Optional[Payment]:
        return await db.get(Payment, payment_id)

    async def get_by_invoice(self, db: AsyncSession, invoice_id: int) -> List[Payment]:
        result = await db.execute(
            select(Payment)
            .where(Payment.invoice_id == invoice_id)
            .order_by(Payment.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, payment_in: PaymentCreate) -> Payment:
        payment = Payment(**payment_in.dict())
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment

    async def update(
        self, db: AsyncSession, payment: Payment, payment_in: PaymentUpdate
    ) -> Payment:
        for field, value in payment_in.dict(exclude_unset=True).items():
            setattr(payment, field, value)
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment

    async def mark_as_paid(
        self, db: AsyncSession, payment_id: int
    ) -> Optional[Payment]:
        payment = await self.get_by_id(db, payment_id)
        if payment:
            payment.status = "paid"
            payment.paid_at = datetime.utcnow()
            db.add(payment)
            await db.commit()
            await db.refresh(payment)
        return payment

    async def delete(self, db: AsyncSession, payment_id: int) -> None:
        payment = await self.get_by_id(db, payment_id)
        if payment:
            await db.delete(payment)
            await db.commit()


payment_crud = PaymentCRUD()
