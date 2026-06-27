import asyncio
import os
import sys
from datetime import date, datetime
from decimal import Decimal

# Add backend directory to system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.db.base
from app.core.config import settings

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

async def add_financial_seeds():
    print("Seeding financial data...")
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is not set.")
        
    from app.modules.financial.models.invoice import Invoice
    from app.modules.financial.models.payment import Payment
    from app.modules.salary.models.contracts import Contract
    from app.modules.salary.models.payroll_cycles import PayrollCycle, PayrollCycleStatus
    from app.modules.salary.models.payroll_records import PayrollRecord

        
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    
    async with AsyncSessionLocal() as db:
        # Create Invoices
        invoice1 = Invoice(
            student_id=1001,
            amount=5000.0,
            due_date=date(2026, 6, 15),
            status="partially_paid",
            description="Tuition Fee Term 1"
        )
        invoice2 = Invoice(
            student_id=1002,
            amount=6000.0,
            due_date=date(2026, 7, 1),
            status="unpaid",
            description="Tuition Fee Term 2"
        )
        db.add_all([invoice1, invoice2])
        await db.flush()
        
        # Create a Payment
        payment1 = Payment(
            invoice_id=invoice1.id,
            external_txn_id="TXN123456",
            gateway="Stripe",
            amount=2000.0,
            status="paid",
            paid_at=datetime(2026, 6, 10, 10, 30, 0)
        )
        db.add(payment1)
        
        # Create a Contract for Teacher 1012
        contract = Contract(
            employee_id=1012,
            base_salary=Decimal("8000.00"),
            allowance=Decimal("1500.00"),
            effective_from=date(2025, 1, 1),
            effective_to=date(2027, 1, 1)
        )
        db.add(contract)
        
        # Create a Payroll Cycle
        cycle = PayrollCycle(
            month=6,
            year=2026,
            status=PayrollCycleStatus.PAID,
            created_by_id=1001,  # GM ID is 1001
            approved_by_id=1001,
            generated_at=datetime(2026, 6, 25, 18, 0, 0)
        )
        db.add(cycle)
        await db.flush()
        
        # Create a Payroll Record
        payroll_record = PayrollRecord(
            cycle_id=cycle.id,
            employee_id=1012,
            base_salary=Decimal("8000.00"),
            allowance=Decimal("1500.00"),
            bonuses=Decimal("500.00"),
            deductions=Decimal("200.00")
        )
        db.add(payroll_record)
        
        await db.commit()
        print("Financial seeds added successfully!")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_financial_seeds())
