from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.permissions.permissions import PermissionCode
from app.modules.staff_evaluations.models import EvaluationStatus
from app.modules.staff_evaluations.schemas import (
    EmployeeEvaluationRead,
    EmployeeEvaluationReadWithDetails,
    EvaluationCommentCreate,
    EvaluationCommentRead,
    EvaluationCycleCreate,
    EvaluationCycleRead,
    EvaluationCycleUpdate,
    EvaluationKPIScoreRead,
    KPICreate,
    KPIRead,
    KPITemplateCreate,
    KPITemplateRead,
    KPITemplateUpdate,
    KPIUpdate,
    ScoreEvaluationRequest,
    StartEvaluationRequest,
)
from app.modules.staff_evaluations.service import staff_evaluation_service
from app.modules.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession

staff_evaluations_router = APIRouter(
    prefix="/staff-evaluations", tags=["Staff Evaluations"]
)


# ========== Evaluation Cycles ==========


@staff_evaluations_router.post(
    "/cycles",
    response_model=EvaluationCycleRead,
    status_code=201,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_CYCLE_MANAGE))
    ],
)
async def create_cycle(
    cycle_in: EvaluationCycleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new evaluation cycle (e.g., Q1 2026)."""
    return await staff_evaluation_service.create_cycle(db, cycle_in)


@staff_evaluations_router.get(
    "/cycles",
    response_model=List[EvaluationCycleRead],
)
async def list_cycles(
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List evaluation cycles."""
    return await staff_evaluation_service.list_cycles(db, is_active)


@staff_evaluations_router.get(
    "/cycles/{cycle_id}",
    response_model=EvaluationCycleRead,
)
async def get_cycle(
    cycle_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific evaluation cycle."""
    return await staff_evaluation_service.get_cycle(db, cycle_id)


@staff_evaluations_router.put(
    "/cycles/{cycle_id}",
    response_model=EvaluationCycleRead,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_CYCLE_MANAGE))
    ],
)
async def update_cycle(
    cycle_id: int,
    cycle_in: EvaluationCycleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an evaluation cycle."""
    return await staff_evaluation_service.update_cycle(db, cycle_id, cycle_in)


# ========== KPI Templates ==========


@staff_evaluations_router.post(
    "/kpi-templates",
    response_model=KPITemplateRead,
    status_code=201,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_KPI_CREATE))
    ],
)
async def create_template(
    template_in: KPITemplateCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new KPI template with optional KPIs."""
    return await staff_evaluation_service.create_template(db, template_in, user)


@staff_evaluations_router.get(
    "/kpi-templates",
    response_model=List[KPITemplateRead],
)
async def list_templates(
    created_by_user_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List KPI templates."""
    return await staff_evaluation_service.list_templates(db, created_by_user_id)


@staff_evaluations_router.get(
    "/kpi-templates/{template_id}",
    response_model=KPITemplateRead,
)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific KPI template with its KPIs."""
    return await staff_evaluation_service.get_template(db, template_id)


@staff_evaluations_router.put(
    "/kpi-templates/{template_id}",
    response_model=KPITemplateRead,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_KPI_EDIT))
    ],
)
async def update_template(
    template_id: int,
    template_in: KPITemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a KPI template."""
    return await staff_evaluation_service.update_template(db, template_id, template_in)


@staff_evaluations_router.delete(
    "/kpi-templates/{template_id}",
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_KPI_DELETE))
    ],
)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a KPI template."""
    await staff_evaluation_service.delete_template(db, template_id)
    return {"message": "تم حذف القالب بنجاح"}


# ========== KPIs ==========


@staff_evaluations_router.post(
    "/kpi-templates/{template_id}/kpis",
    response_model=KPIRead,
    status_code=201,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_KPI_CREATE))
    ],
)
async def add_kpi(
    template_id: int,
    kpi_in: KPICreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a KPI to a template."""
    return await staff_evaluation_service.add_kpi(db, template_id, kpi_in)


@staff_evaluations_router.get(
    "/kpi-templates/{template_id}/kpis",
    response_model=List[KPIRead],
)
async def get_kpis(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all KPIs for a template."""
    return await staff_evaluation_service.get_kpis(db, template_id)


@staff_evaluations_router.put(
    "/kpi-templates/{template_id}/kpis/{kpi_id}",
    response_model=KPIRead,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_KPI_EDIT))
    ],
)
async def update_kpi(
    template_id: int,
    kpi_id: int,
    kpi_in: KPIUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a KPI."""
    return await staff_evaluation_service.update_kpi(db, template_id, kpi_id, kpi_in)


@staff_evaluations_router.delete(
    "/kpi-templates/{template_id}/kpis/{kpi_id}",
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_EVALUATION_KPI_DELETE))
    ],
)
async def delete_kpi(
    template_id: int,
    kpi_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a KPI from a template."""
    await staff_evaluation_service.delete_kpi(db, template_id, kpi_id)
    return {"message": "تم حذف المؤشر بنجاح"}


# ========== Evaluations ==========


@staff_evaluations_router.post(
    "/evaluations/start",
    response_model=EmployeeEvaluationReadWithDetails,
    status_code=201,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_CREATE))],
)
async def start_evaluation(
    request: StartEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Start a new evaluation for an employee."""
    return await staff_evaluation_service.start_evaluation(db, request, user)


@staff_evaluations_router.get(
    "/evaluations",
    response_model=List[EmployeeEvaluationReadWithDetails],
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_VIEW))],
)
async def list_evaluations(
    cycle_id: Optional[int] = Query(None),
    employee_user_id: Optional[int] = Query(None),
    status: Optional[EvaluationStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List evaluations with filters."""
    return await staff_evaluation_service.list_evaluations(
        db, cycle_id, employee_user_id, user.id, status
    )


@staff_evaluations_router.get(
    "/evaluations/{evaluation_id}",
    response_model=EmployeeEvaluationReadWithDetails,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_VIEW))],
)
async def get_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get an evaluation with full details."""
    return await staff_evaluation_service.get_evaluation(db, evaluation_id)


@staff_evaluations_router.post(
    "/evaluations/{evaluation_id}/score",
    response_model=List[EvaluationKPIScoreRead],
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_CREATE))],
)
async def score_evaluation(
    evaluation_id: int,
    request: ScoreEvaluationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update KPI scores for an evaluation."""
    return await staff_evaluation_service.score_evaluation(db, evaluation_id, request)


@staff_evaluations_router.post(
    "/evaluations/{evaluation_id}/submit",
    response_model=EmployeeEvaluationRead,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_SUBMIT))],
)
async def submit_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Submit an evaluation. This calculates the final score."""
    return await staff_evaluation_service.submit_evaluation(db, evaluation_id)


@staff_evaluations_router.post(
    "/evaluations/{evaluation_id}/approve",
    response_model=EmployeeEvaluationRead,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_APPROVE))],
)
async def approve_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Approve a submitted evaluation."""
    return await staff_evaluation_service.approve_evaluation(db, evaluation_id)


@staff_evaluations_router.get(
    "/evaluations/employee/{user_id}",
    response_model=List[EmployeeEvaluationRead],
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_VIEW))],
)
async def get_employee_evaluations(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all evaluations for a specific employee."""
    return await staff_evaluation_service.list_evaluations(db, employee_user_id=user_id)


# ========== Comments ==========


@staff_evaluations_router.post(
    "/evaluations/{evaluation_id}/comments",
    response_model=EvaluationCommentRead,
    status_code=201,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_CREATE))],
)
async def add_comment(
    evaluation_id: int,
    comment_in: EvaluationCommentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a comment to an evaluation."""
    return await staff_evaluation_service.add_comment(db, evaluation_id, comment_in)


@staff_evaluations_router.get(
    "/evaluations/{evaluation_id}/comments",
    response_model=List[EvaluationCommentRead],
    dependencies=[Depends(require_permission(PermissionCode.STAFF_EVALUATION_VIEW))],
)
async def get_comments(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all comments for an evaluation."""
    return await staff_evaluation_service.get_comments(db, evaluation_id)
