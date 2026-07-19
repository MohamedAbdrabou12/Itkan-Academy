from decimal import Decimal

from app.modules.enrolments.schemas.enrolment import EnrolmentRead
from app.modules.users.schemas import UserRead
from pydantic import BaseModel


class EnrolmentPricingPlanCreate(BaseModel):
    curriculum_id: int
    branch_id: int | None = None
    name: str
    monthly_price: str
    start_month: int
    end_month: int


class EnrolmentPricingPlanRead(BaseModel):
    id: int
    curriculum_id: int
    curriculum_name: str
    branch_id: int | None = None
    branch_name: str | None = None
    name: str
    monthly_price: Decimal
    start_month: int
    end_month: int


class EnrolmentPricingPlanReadWithEnrolments(EnrolmentPricingPlanRead):
    enrolments: list[EnrolmentRead]


class EnrolmentPricingPlanReadAllParent(BaseModel):
    pricing_plans: list[EnrolmentPricingPlanReadWithEnrolments]
    children: list[UserRead]


class EnrolmentPricingPlanUpdate(BaseModel):
    curriculum_id: int | None = None
    branch_id: int | None = None
    name: str | None = None
    monthly_price: str | None = None
    start_month: int | None = None
    end_month: int | None = None
