import typing
from decimal import Context, Decimal
from typing import Annotated

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.enrolments.crud.enrolment import enrolment_crud as crud
from app.modules.enrolments.crud.pricing_plan import enrolment_pricing_plan_crud
from app.modules.enrolments.helpers import enrolment as helpers
from app.modules.enrolments.schemas import enrolment as schemas
from app.modules.payments import paymob
from app.modules.permissions.permissions import PermissionCode
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.datastructures import URL
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from .pricing_plan import enrolment_pricing_plans_router

enrolments_router = APIRouter(prefix="/enrolments", tags=["Enrolments"])
enrolments_router.include_router(enrolment_pricing_plans_router)

base_url = URL("https://z3jtyg-ip-102-41-67-53.tunnelmole.net/api/v1")


def get_first_and_last_name(user: User):
    name_parts = user.full_name.split(" ")
    return name_parts[0], name_parts[-1]


@enrolments_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENTS_ADD))],
)
async def create_enrolment(
    db: Annotated[AsyncSession, Depends(get_db)], data: schemas.EnrolmentCreate
) -> None:
    _ = crud.create(db, data)
    await db.commit()


@enrolments_router.post("/enrol", status_code=status.HTTP_200_OK)
async def enrol(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    data: schemas.EnrolmentEnrol,
):
    if (user.student is None or data.student_id != user.id) and (
        user.parent is None
        or data.student_id not in map(lambda child: child.user_id, user.parent.children)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="لا يمكنك تسجيل هذا الطالب"
        )

    pricing_plan = await enrolment_pricing_plan_crud.get_by_id(db, data.pricing_plan_id)
    if pricing_plan is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="لم يتم العثور على خطة التسعير"
        )

    if await crud.exists_by_curriculum_and_student_id(
        db, pricing_plan.curriculum_id, data.student_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="هذا الطالب مسجل بالفعل"
        )

    amount = pricing_plan.monthly_price
    first_name, last_name = get_first_and_last_name(user)

    notification_url = base_url.replace(
        path=base_url.path + "/enrolments/enrol/webhook/"
    ).replace_query_params(student_id=data.student_id, pricing_plan_id=pricing_plan.id)

    checkout_url = await paymob.create_paymob_intention(
        amount=amount,
        item_name=pricing_plan.curriculum.name,
        item_description=pricing_plan.curriculum.description,
        first_name=first_name,
        last_name=last_name,
        email=user.email or "",
        phone=user.phone or "",
        notification_url=notification_url.components.geturl(),
        redirection_url=data.redirection_url,
        special_reference=f"enrol-{pricing_plan.id}-{data.student_id}-{amount}-{user.id}",
        expiration=3600,
    )

    return schemas.EnrolmentPaymentResponse(checkout_url=checkout_url.components.geturl())


@enrolments_router.post("/enrol/webhook", status_code=status.HTTP_200_OK)
async def enrol_webhook(
    db: Annotated[AsyncSession, Depends(get_db)],
    student_id: Annotated[int, Query()],
    pricing_plan_id: Annotated[int, Query()],
    hmac: Annotated[str, Query()],
    request: Request,
):
    # TODO: do logging and stuff when anything goes wrong
    data = await paymob.webhook_hmac_check(hmac, request)
    obj: dict[str, typing.Any] = data.get("obj", {})  # pyright: ignore[reportAny]
    success: bool = obj.get("success") and not obj.get("error_occured") or False
    if not success:
        return

    pricing_plan = await enrolment_pricing_plan_crud.get_by_id(db, pricing_plan_id)
    if pricing_plan is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown pricing plan")

    amount_cents: int = obj.get("amount_cents", 0)  # pyright: ignore[reportAny]
    amount = Decimal(amount_cents / 100, context=Context(prec=2))
    if amount != pricing_plan.monthly_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment amount"
        )

    _ = crud.create(
        db,
        schemas.EnrolmentCreate(
            pricing_plan_id=pricing_plan_id, student_id=student_id, months_paid=1
        ),
    )
    await db.commit()


@enrolments_router.post("/{id}/monthly-fee", status_code=status.HTTP_200_OK)
async def pay_monthly_fee(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    redirection_url: Annotated[str, Query()],
    id: int,
) -> schemas.EnrolmentPaymentResponse:
    enrolment = await crud.get_by_id(db, id)
    if enrolment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrolment not found")

    if (user.student is None or enrolment.student_id != user.id) and (
        user.parent is None
        or enrolment.student_id not in map(lambda child: child.user_id, user.parent.children)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="لم يتم الالتحاق بك")

    amount = helpers.calculate_enrolment_monthly_fee(enrolment)
    if amount.is_zero():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="قد تم الدفع لهذا الشهر من قبل"
        )

    first_name, last_name = get_first_and_last_name(user)

    notification_url = base_url.replace(
        path=base_url.path + "/enrolments/" + str(enrolment.id) + "/monthly-fee/webhook/"
    )

    checkout_url = await paymob.create_paymob_intention(
        amount=amount,
        item_name=enrolment.pricing_plan.curriculum.name,
        item_description=enrolment.pricing_plan.curriculum.description,
        first_name=first_name,
        last_name=last_name,
        email=user.email or "",
        phone=user.phone or "",
        notification_url=notification_url.components.geturl(),
        redirection_url=redirection_url,
        special_reference=f"monthly-{enrolment.months_paid}-{enrolment.pricing_plan_id}-{enrolment.student_id}-{amount}-{user.id}",
        expiration=3600,
    )

    return schemas.EnrolmentPaymentResponse(checkout_url=checkout_url.components.geturl())


@enrolments_router.post("/{id}/monthly-fee/webhook")
async def monthly_fee_payment_webhook(
    db: Annotated[AsyncSession, Depends(get_db)],
    id: int,
    hmac: Annotated[str, Query()],
    request: Request,
) -> None:
    enrolment = await crud.get_by_id(db, id)
    if enrolment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown enrolment ID")

    # TODO: do logging and stuff when anything goes wrong
    data = await paymob.webhook_hmac_check(hmac, request)
    obj: dict[str, typing.Any] = data.get("obj", {})  # pyright: ignore[reportAny]
    success: bool = obj.get("success") and not obj.get("error_occured") or False
    if not success:
        return

    amount_cents: int = obj.get("amount_cents", 0)  # pyright: ignore[reportAny]
    amount = Decimal(amount_cents / 100, context=Context(prec=2))
    if amount % enrolment.pricing_plan.monthly_price != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment amount"
        )

    enrolment.months_paid += int(amount / enrolment.pricing_plan.monthly_price)

    db.add(enrolment)
    await db.commit()


@enrolments_router.get(
    "/",
    response_model=Page[schemas.EnrolmentRead],
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENTS_VIEW))],
)
async def get_enrolments(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str, Query()] = "id",
    sort_order: Annotated[str, Query()] = "asc",
):
    return await crud.get_all(db=db, search=search, sort_by=sort_by, sort_order=sort_order)


@enrolments_router.put(
    "/{id}",
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENTS_EDIT))],
)
async def update_enrolment(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, data: schemas.EnrolmentUpdate
):
    await crud.update(db, id, data)
    await db.commit()


@enrolments_router.delete(
    "/{id}",
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_ENROLMENTS_DELETE))],
)
async def delete_enrolment(db: Annotated[AsyncSession, Depends(get_db)], id: int):
    await crud.delete(db, id)
    await db.commit()
