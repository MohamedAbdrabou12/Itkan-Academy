from pydantic import BaseModel


class EnrolmentCreate(BaseModel):
    pricing_plan_id: int
    student_id: int
    months_paid: int


class EnrolmentUpdate(EnrolmentCreate):
    pricing_plan_id: int
    student_id: int
    months_paid: int


class EnrolmentEnrol(BaseModel):
    pricing_plan_id: int
    student_id: int
    redirection_url: str


class EnrolmentPaymentResponse(BaseModel):
    checkout_url: str


class EnrolmentRead(BaseModel):
    id: int
    pricing_plan_id: int
    pricing_plan_name: str
    student_id: int
    student_full_name: str
    start_month: int
    end_month: int
    months_paid: int
