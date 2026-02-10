from datetime import date as dt_date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.modules.staff_evaluations.models import EvaluationStatus
from app.modules.users.schemas import UserRead


# ========== Evaluation Cycle Schemas ==========


class EvaluationCycleBase(BaseModel):
    name: str = Field(..., max_length=100, description="Cycle name, e.g. 'Q1 2026'")
    start_date: dt_date
    end_date: dt_date
    is_active: bool = True


class EvaluationCycleCreate(EvaluationCycleBase):
    pass


class EvaluationCycleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    start_date: Optional[dt_date] = None
    end_date: Optional[dt_date] = None
    is_active: Optional[bool] = None


class EvaluationCycleRead(EvaluationCycleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== KPI Schemas ==========


class KPIBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    weight: Decimal = Field(..., ge=0, le=100, description="Weight percentage (0-100)")
    max_score: int = Field(default=5, ge=1)


class KPICreate(KPIBase):
    pass


class KPIUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    weight: Optional[Decimal] = Field(None, ge=0, le=100)
    max_score: Optional[int] = Field(None, ge=1)


class KPIRead(KPIBase):
    id: int
    template_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== KPI Template Schemas ==========


class KPITemplateBase(BaseModel):
    name: str = Field(..., max_length=200)


class KPITemplateCreate(KPITemplateBase):
    kpis: Optional[List[KPICreate]] = None


class KPIBatchItem(KPICreate):
    id: Optional[int] = None


class KPITemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    kpis: Optional[List[KPIBatchItem]] = None


class KPITemplateRead(KPITemplateBase):
    id: int
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    kpis: Optional[List[KPIRead]] = None

    class Config:
        from_attributes = True


class KPITemplateReadWithCreator(KPITemplateRead):
    created_by: Optional[UserRead] = None


# ========== Evaluation KPI Score Schemas ==========


class EvaluationKPIScoreBase(BaseModel):
    kpi_id: int
    score: Decimal = Field(..., ge=0, description="Score value")


class EvaluationKPIScoreCreate(EvaluationKPIScoreBase):
    pass


class EvaluationKPIScoreUpdate(BaseModel):
    score: Decimal = Field(..., ge=0)


class EvaluationKPIScoreRead(EvaluationKPIScoreBase):
    id: int
    evaluation_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EvaluationKPIScoreReadWithKPI(EvaluationKPIScoreRead):
    kpi: Optional[KPIRead] = None


# ========== Evaluation Comment Schemas ==========


class EvaluationCommentBase(BaseModel):
    comment: str = Field(..., min_length=1)


class EvaluationCommentCreate(EvaluationCommentBase):
    pass


class EvaluationCommentRead(EvaluationCommentBase):
    id: int
    evaluation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Employee Evaluation Schemas ==========


class EmployeeEvaluationBase(BaseModel):
    employee_user_id: int
    cycle_id: int
    template_id: int
    branch_id: Optional[int] = None


class StartEvaluationRequest(EmployeeEvaluationBase):
    """Request to start a new evaluation."""

    pass


class ScoreEvaluationRequest(BaseModel):
    """Request to score KPIs for an evaluation."""

    scores: List[EvaluationKPIScoreCreate]

    @field_validator("scores")
    @classmethod
    def validate_scores_not_empty(cls, v: List[EvaluationKPIScoreCreate]):
        if not v:
            raise ValueError("At least one KPI score is required")
        return v


class EmployeeEvaluationRead(EmployeeEvaluationBase):
    id: int
    evaluator_user_id: int
    status: EvaluationStatus
    final_score: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeEvaluationReadWithDetails(EmployeeEvaluationRead):
    employee: Optional[UserRead] = None
    evaluator: Optional[UserRead] = None
    cycle: Optional[EvaluationCycleRead] = None
    template: Optional[KPITemplateRead] = None
    kpi_scores: Optional[List[EvaluationKPIScoreReadWithKPI]] = None
    comments: Optional[List[EvaluationCommentRead]] = None


# ========== Response Schemas ==========


class EvaluationStartResponse(BaseModel):
    success: bool
    message: str
    evaluation: Optional[EmployeeEvaluationRead] = None


class EvaluationScoreResponse(BaseModel):
    success: bool
    message: str
    scores: Optional[List[EvaluationKPIScoreRead]] = None


class EvaluationSubmitResponse(BaseModel):
    success: bool
    message: str
    final_score: Optional[Decimal] = None
    evaluation: Optional[EmployeeEvaluationRead] = None


# ========== Validation Helper Schemas ==========


class KPIWeightValidation(BaseModel):
    """Used to validate that KPI weights sum to 100."""

    kpis: List[KPICreate]

    @field_validator("kpis")
    @classmethod
    def validate_weights_sum_to_100(cls, v: List[KPICreate]):
        if not v:
            return v
        total_weight = sum(kpi.weight for kpi in v)
        if total_weight != Decimal("100"):
            raise ValueError(f"KPI weights must sum to 100, got {total_weight}")
        return v
