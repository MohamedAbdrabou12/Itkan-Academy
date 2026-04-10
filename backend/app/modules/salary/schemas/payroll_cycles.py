from app.modules.salary.models.payroll_cycles import PayrollCycleStatus
from fastapi_pagination import Page
from pydantic import BaseModel


class PayrollCycleGetData(BaseModel):
    id: int
    month: int
    year: int
    status: PayrollCycleStatus
    created_by_name: str
    approved_by_name: str | None



class PayrollRecordGetData(BaseModel):
    id: int
    employee_name: str
    role_name_ar: str | None = None
    base_salary: str
    allowance: str
    bonuses: str
    deductions: str
    paid_at: str | None = None
    total: str


class PayrollRecordGetDataPage(BaseModel):
    items_total: str
    page_info: Page[PayrollRecordGetData]


class PayrollRecordEditData(BaseModel):
    bonuses: str | None = None
    deductions: str | None = None
