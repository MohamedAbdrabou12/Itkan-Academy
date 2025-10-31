from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.financial.schemas.payment import (
    PaymentCreate,
    PaymentRead,
    PaymentUpdate,
)
from app.modules.financial.crud.payment import payment_crud

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get(
    "/",
    response_model=List[PaymentRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("payment:view")),
    ],
)
async def list_payments(db: AsyncSession = Depends(get_db)):
    return await payment_crud.get_all(db)


@router.get(
    "/{payment_id}",
    response_model=PaymentRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("payment:view")),
    ],
)
async def get_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    payment = await payment_crud.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get(
    "/invoice/{invoice_id}",
    response_model=List[PaymentRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("payment:view")),
    ],
)
async def get_payments_by_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    return await payment_crud.get_by_invoice(db, invoice_id)


@router.post(
    "/",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("payment:create")),
    ],
)
async def create_payment(payment_in: PaymentCreate, db: AsyncSession = Depends(get_db)):
    return await payment_crud.create(db, payment_in)


@router.put(
    "/{payment_id}",
    response_model=PaymentRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("payment:update")),
    ],
)
async def update_payment(
    payment_id: int, payment_in: PaymentUpdate, db: AsyncSession = Depends(get_db)
):
    payment = await payment_crud.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return await payment_crud.update(db, payment, payment_in)


@router.put(
    "/{payment_id}/mark-paid",
    response_model=PaymentRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("payment:update")),
    ],
)
async def mark_payment_as_paid(payment_id: int, db: AsyncSession = Depends(get_db)):
    payment = await payment_crud.mark_as_paid(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("payment:delete")),
    ],
)
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    await payment_crud.delete(db, payment_id)
    return None
