from typing import Annotated

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.enrolments.crud.pricing_plan import enrolment_pricing_plan_crud as crud
from app.modules.enrolments.schemas import pricing_plan as schemas
from app.modules.permissions.permissions import PermissionCode
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

enrolment_pricing_plans_router = APIRouter(prefix="/pricing-plans", tags=["Enrolment Pricing"])


@enrolment_pricing_plans_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENT_PRICING_PLANS_ADD))],
)
async def create_pricing_plan(
    db: Annotated[AsyncSession, Depends(get_db)],
    data: schemas.EnrolmentPricingPlanCreate,
):
    _ = crud.create(db, data)
    await db.commit()


@enrolment_pricing_plans_router.get(
    "/",
    response_model=Page[schemas.EnrolmentPricingPlanRead],
    dependencies=[
        Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENT_PRICING_PLANS_VIEW))
    ],
)
async def get_pricing_plans(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str, Query()] = "id",
    sort_order: Annotated[str, Query()] = "asc",
):
    return await crud.get_all(
        db=db,
        branch_id=getattr(request.state, "branch_id", None),
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@enrolment_pricing_plans_router.get(
    "/parent", response_model=schemas.EnrolmentPricingPlanReadAllParent
)
async def parent_get_pricing_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    owned_only: Annotated[bool, Query()] = False,
):
    if user.parent is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="لست والدا")

    return await crud.get_all_parent(db, user.parent, owned_only)


@enrolment_pricing_plans_router.put(
    "/{id}",
    dependencies=[
        Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENT_PRICING_PLANS_EDIT))
    ],
)
async def update_pricing_plan(
    db: Annotated[AsyncSession, Depends(get_db)],
    id: int,
    data: schemas.EnrolmentPricingPlanUpdate,
) -> None:
    await crud.update(db, id, data)
    await db.commit()


@enrolment_pricing_plans_router.delete(
    "/{id}",
    dependencies=[
        Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENT_PRICING_PLANS_DELETE))
    ],
)
async def delete_pricing_plan(db: Annotated[AsyncSession, Depends(get_db)], id: int):
    await crud.delete(db, id)
    await db.commit()
