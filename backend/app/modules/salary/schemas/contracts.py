from pydantic import BaseModel


class ContractRegisterData(BaseModel):
    employee_id: int
    base_salary: str
    allowance: str
    effective_from: str
    effective_to: str


class ContractGetData(ContractRegisterData, BaseModel):
    id: int
    employee_full_name: str
    role_name_ar: str | None = None
    created_at: str
    updated_at: str


class ContractEditData(BaseModel):
    employee_id: int | None = None
    base_salary: str | None = None
    allowance: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
