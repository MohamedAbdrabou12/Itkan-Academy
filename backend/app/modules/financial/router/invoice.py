from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.financial.schemas.invoice import (
    InvoiceCreate,
    InvoiceRead,
    InvoiceUpdate,
)
from app.modules.financial.crud.invoice import invoice_crud

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get(
    "/",
    response_model=List[InvoiceRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("invoice:view")),
    ],
)
async def list_invoices(db: AsyncSession = Depends(get_db)):
    return await invoice_crud.get_all(db)


@router.get(
    "/{invoice_id}",
    response_model=InvoiceRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("invoice:view")),
    ],
)
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    invoice = await invoice_crud.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get(
    "/student/{student_id}",
    response_model=List[InvoiceRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("invoice:view")),
    ],
)
async def get_invoices_by_student(student_id: int, db: AsyncSession = Depends(get_db)):
    return await invoice_crud.get_by_student(db, student_id)


@router.post(
    "/",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("invoice:create")),
    ],
)
async def create_invoice(invoice_in: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    return await invoice_crud.create(db, invoice_in)


@router.put(
    "/{invoice_id}",
    response_model=InvoiceRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("invoice:update")),
    ],
)
async def update_invoice(
    invoice_id: int, invoice_in: InvoiceUpdate, db: AsyncSession = Depends(get_db)
):
    invoice = await invoice_crud.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return await invoice_crud.update(db, invoice, invoice_in)


@router.delete(
    "/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("invoice:delete")),
    ],
)
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    await invoice_crud.delete(db, invoice_id)
    return None
