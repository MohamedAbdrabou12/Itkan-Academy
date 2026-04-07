from typing import Annotated

from app.core.auth import get_current_user, get_current_user_id
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.permissions.permissions import PermissionCode
from app.modules.salary.crud.payroll_cycles import payroll_cycles_crud
from app.modules.salary.models.payroll_cycles import PayrollCycleStatus
from app.modules.salary.schemas.payroll_cycles import (
    PayrollCycleGetData,
    PayrollRecordEditData,
    PayrollRecordGetDataPage,
)
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

payroll_cycles_router = APIRouter(prefix="/payroll/cycles", tags=["Payroll Cycles"])


@payroll_cycles_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PAYROLL_CYCLES_VIEW))],
)
async def get_all_payroll_cycles(
    db: Annotated[AsyncSession, Depends(get_db)],
    sort_by: Annotated[str, Query()] = "id",
    sort_order: Annotated[str, Query()] = "asc",
    page: Annotated[int, Query()] = 1,
    size: Annotated[int, Query()] = 100,
) -> Page[PayrollCycleGetData]:
    return await payroll_cycles_crud.get_all_cycles(
        db, sort_by=sort_by, sort_order=sort_order, page=page, size=size
    )


@payroll_cycles_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PAYROLL_CYCLES_VIEW))],
)
async def get_payroll_cycle(
    db: Annotated[AsyncSession, Depends(get_db)], id: int
) -> PayrollCycleGetData:
    cycle = await payroll_cycles_crud.get_cycle_by_id(db, id)
    return PayrollCycleGetData(
        id=cycle.id,
        month=cycle.month,
        year=cycle.year,
        status=cycle.status,
        created_by_name=cycle.created_by.full_name,
        approved_by_name=None if cycle.approved_by is None else cycle.approved_by.full_name,
    )


@payroll_cycles_router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PAYROLL_CYCLES_ADD))],
)
async def generate_payroll_cycle(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    month: Annotated[int, Query()],
    year: Annotated[int, Query()],
) -> None:
    if await payroll_cycles_crud.cycle_already_exists(db, month, year):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="توجد دورة مرتب مسجلة لهذا الفرع وهذا اليوم بالفعل",
        )

    await payroll_cycles_crud.generate_cycle(db, month, year, current_user_id)


@payroll_cycles_router.put(
    "/{cycle_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PAYROLL_CYCLES_EDIT))],
)
async def edit_payroll_cycle(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    cycle_id: int,
    status: Annotated[PayrollCycleStatus, Query()],
) -> None:
    await payroll_cycles_crud.edit_cycle(db, current_user, cycle_id, status)
    await db.commit()


@payroll_cycles_router.delete(
    "/{cycle_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PAYROLL_CYCLES_DELETE))],
)
async def delete_payroll_cycle(db: Annotated[AsyncSession, Depends(get_db)], cycle_id: int) -> None:
    cycle = await payroll_cycles_crud.get_cycle_by_id(db, cycle_id)
    if cycle.status == PayrollCycleStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الدورة مقبولة وليس لك المقدرة على مسحها",
        )

    await payroll_cycles_crud.delete_cycle(db, cycle_id)
    await db.commit()


@payroll_cycles_router.get(
    "/records/{cycle_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PAYROLL_CYCLES_VIEW))],
)
async def get_payroll_records(
    db: Annotated[AsyncSession, Depends(get_db)],
    cycle_id: int,
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str, Query()] = "id",
    sort_order: Annotated[str, Query()] = "asc",
    page: Annotated[int, Query()] = 1,
    size: Annotated[int, Query()] = 100,
) -> PayrollRecordGetDataPage:
    return await payroll_cycles_crud.get_cycle_records(
        db,
        cycle_id=cycle_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        size=size,
    )


@payroll_cycles_router.put(
    "/edit-record/{record_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PAYROLL_CYCLES_EDIT))],
)
async def edit_payroll_record(
    db: Annotated[AsyncSession, Depends(get_db)],
    record_id: int,
    data: PayrollRecordEditData,
) -> None:
    record = await payroll_cycles_crud.get_cycle_record_by_id(db, record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payroll record not found"
        )

    if record.cycle.status in (
        PayrollCycleStatus.LOCKED,
        PayrollCycleStatus.APPROVED,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="قد تم قبول أو غلق الدورة للقبول وليس لديك القدرة على أن تعدلها",
        )

    await payroll_cycles_crud.edit_cycle_record(db, record, data)
    await db.commit()
