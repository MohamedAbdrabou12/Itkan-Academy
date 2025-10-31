from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.modules.financial.models.invoice import Invoice
from app.modules.financial.schemas.invoice import InvoiceCreate, InvoiceUpdate


class InvoiceCRUD:
    async def get_all(self, db: AsyncSession) -> List[Invoice]:
        result = await db.execute(select(Invoice).order_by(Invoice.created_at.desc()))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, invoice_id: int) -> Optional[Invoice]:
        return await db.get(Invoice, invoice_id)

    async def get_by_student(self, db: AsyncSession, student_id: int) -> List[Invoice]:
        result = await db.execute(
            select(Invoice)
            .where(Invoice.student_id == student_id)
            .order_by(Invoice.due_date)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, invoice_in: InvoiceCreate) -> Invoice:
        invoice = Invoice(**invoice_in.dict())
        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)
        return invoice

    async def update(
        self, db: AsyncSession, invoice: Invoice, invoice_in: InvoiceUpdate
    ) -> Invoice:
        for field, value in invoice_in.dict(exclude_unset=True).items():
            setattr(invoice, field, value)
        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)
        return invoice

    async def delete(self, db: AsyncSession, invoice_id: int) -> None:
        invoice = await self.get_by_id(db, invoice_id)
        if invoice:
            await db.delete(invoice)
            await db.commit()


invoice_crud = InvoiceCRUD()
