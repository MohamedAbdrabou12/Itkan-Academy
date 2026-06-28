from datetime import date, datetime, time
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.modules.financial.models.payment import Payment
from app.modules.financial.models.invoice import Invoice
from app.modules.students.models import Student
from app.modules.users.models import User
from app.modules.salary.models.payroll_records import PayrollRecord
from app.modules.salary.models.payroll_cycles import PayrollCycle
from sqlalchemy.ext.asyncio import AsyncSession

async def query_revenue_by_branch(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: Optional[List[int]] = None,
):
    start_dt = datetime.combine(date.fromisoformat(date_from), time.min)
    end_dt = datetime.combine(date.fromisoformat(date_to), time.max)
    
    query = (
        select(Payment)
        .join(Invoice, Invoice.id == Payment.invoice_id)
        .where(Payment.status == "paid")
        .where(Payment.paid_at.between(start_dt, end_dt))
        .options(
            selectinload(Payment.invoice)
            .selectinload(Invoice.student)
            .selectinload(Student.user)
            .selectinload(User.branches)
        )
    )
    
    result = await db.execute(query)
    payments = result.scalars().unique().all()
    
    branch_map = {}
    
    if branch_ids:
        from app.modules.branches.models import Branch
        b_query = select(Branch).where(Branch.id.in_(branch_ids))
        b_res = await db.execute(b_query)
        for b in b_res.scalars().all():
            branch_map[b.id] = {
                "branch_id": b.id,
                "branch_name": b.name,
                "total_revenue": 0.0,
                "payment_count": 0
            }
            
    for p in payments:
        student = p.invoice.student
        if not student or not student.user:
            continue
        branches = student.user.branches
        if not branches:
            continue
            
        for b in branches:
            if branch_ids and b.id not in branch_ids:
                continue
            if b.id not in branch_map:
                branch_map[b.id] = {
                    "branch_id": b.id,
                    "branch_name": b.name,
                    "total_revenue": 0.0,
                    "payment_count": 0
                }
            branch_map[b.id]["total_revenue"] += float(p.amount) if p.amount is not None else 0.0
            branch_map[b.id]["payment_count"] += 1
            
    return list(branch_map.values())

async def query_outstanding_tuition(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: Optional[List[int]] = None,
    student_ids: Optional[List[int]] = None,
):
    query = (
        select(Invoice)
        .where(Invoice.status != "paid")
        .where(Invoice.due_date.between(date.fromisoformat(date_from), date.fromisoformat(date_to)))
        .options(
            selectinload(Invoice.student)
            .selectinload(Student.user)
            .selectinload(User.branches)
        )
    )
    
    result = await db.execute(query)
    invoices = result.scalars().unique().all()
    
    filtered_invoices = []
    for inv in invoices:
        student = inv.student
        if not student or not student.user:
            continue
            
        if student_ids and student.id not in student_ids:
            continue
            
        if branch_ids:
            student_branch_ids = [b.id for b in student.user.branches]
            if not any(bid in branch_ids for bid in student_branch_ids):
                continue
                
        filtered_invoices.append(inv)
        
    return filtered_invoices

async def query_teacher_payroll(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: Optional[List[int]] = None,
    teacher_ids: Optional[List[int]] = None,
):
    from_date = date.fromisoformat(date_from)
    to_date = date.fromisoformat(date_to)
    
    query = (
        select(PayrollRecord)
        .join(PayrollCycle, PayrollCycle.id == PayrollRecord.cycle_id)
        .join(User, User.id == PayrollRecord.employee_id)
        .where(User.teacher.has())
        .options(
            selectinload(PayrollRecord.cycle),
            selectinload(PayrollRecord.employee).selectinload(User.branches)
        )
    )
    
    result = await db.execute(query)
    records = result.scalars().unique().all()
    
    filtered_records = []
    for rec in records:
        cycle = rec.cycle
        cycle_val = cycle.year * 12 + cycle.month
        start_val = from_date.year * 12 + from_date.month
        end_val = to_date.year * 12 + to_date.month
        
        if not (start_val <= cycle_val <= end_val):
            continue
            
        employee = rec.employee
        if not employee:
            continue
            
        if teacher_ids and employee.id not in teacher_ids:
            continue
            
        if branch_ids:
            emp_branch_ids = [b.id for b in employee.branches]
            if not any(bid in branch_ids for bid in emp_branch_ids):
                continue
                
        filtered_records.append(rec)
        
    return filtered_records

async def query_student_payments(
    db: AsyncSession,
    date_from: str,
    date_to: str,
    branch_ids: Optional[List[int]] = None,
    student_ids: Optional[List[int]] = None,
):
    start_dt = datetime.combine(date.fromisoformat(date_from), time.min)
    end_dt = datetime.combine(date.fromisoformat(date_to), time.max)
    
    query = (
        select(Payment)
        .join(Invoice, Invoice.id == Payment.invoice_id)
        .where(Payment.created_at.between(start_dt, end_dt))
        .options(
            selectinload(Payment.invoice)
            .selectinload(Invoice.student)
            .selectinload(Student.user)
            .selectinload(User.branches)
        )
        .order_by(Payment.created_at.desc())
    )
    
    result = await db.execute(query)
    payments = result.scalars().unique().all()
    
    filtered_payments = []
    for p in payments:
        student = p.invoice.student
        if not student or not student.user:
            continue
            
        if student_ids and student.id not in student_ids:
            continue
            
        if branch_ids:
            student_branch_ids = [b.id for b in student.user.branches]
            if not any(bid in branch_ids for bid in student_branch_ids):
                continue
                
        filtered_payments.append(p)
        
    return filtered_payments
