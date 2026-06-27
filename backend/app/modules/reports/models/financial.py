from typing import Optional
from pydantic import BaseModel

class RevenueByBranchReportData(BaseModel):
    branch_id: int
    branch_name: str
    total_revenue: float
    payment_count: int

class OutstandingTuitionReportData(BaseModel):
    invoice_id: int
    branch_id: int
    branch_name: str
    student_id: int
    student_name: str
    amount: float
    due_date: str
    status: str
    description: Optional[str] = None

class TeacherPayrollReportData(BaseModel):
    record_id: int
    cycle_id: int
    cycle_name: str
    employee_id: int
    employee_name: str
    branch_names: str
    base_salary: float
    allowance: float
    bonuses: float
    deductions: float
    net_salary: float

class StudentPaymentReportData(BaseModel):
    payment_id: int
    invoice_id: int
    student_id: int
    student_name: str
    branch_name: str
    amount: float
    status: str
    gateway: Optional[str] = None
    external_txn_id: Optional[str] = None
    paid_at: Optional[str] = None
