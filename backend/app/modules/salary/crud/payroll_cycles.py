import datetime
from collections.abc import Sequence
from decimal import Decimal

from app.core.authorization import generate_generic_permission, get_user_permissions
from app.modules.permissions.permissions import PermissionCode
from app.modules.roles.models import Role
from app.modules.salary.crud.contracts import contracts_crud
from app.modules.salary.models.payroll_cycles import (
    PayrollCycle,
    PayrollCycleStatus,
)
from app.modules.salary.models.payroll_records import PayrollRecord
from app.modules.salary.schemas.payroll_cycles import (
    PayrollCycleGetData,
    PayrollRecordEditData,
    PayrollRecordGetData,
    PayrollRecordGetDataPage,
)
from app.modules.users.models import User
from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import and_, asc, delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class PayrollCyclesCrud:
    async def get_all_cycles(
        self,
        db: AsyncSession,
        sort_by: str = "id",
        sort_order: str = "asc",
        page: int = 1,
        size: int = 100,
    ) -> Page[PayrollCycleGetData]:
        query = select(PayrollCycle).options(
            joinedload(PayrollCycle.created_by),
            joinedload(PayrollCycle.approved_by),
        )

        sort_columns = {
            "id": PayrollCycle.id,
            "month": PayrollCycle.month,
            "year": PayrollCycle.year,
            "status": PayrollCycle.status,
        }

        sort_column = sort_columns.get(sort_by, PayrollCycle.id)
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        async def items_transformer(items: Sequence[PayrollCycle]) -> Sequence[PayrollCycleGetData]:
            return [
                PayrollCycleGetData(
                    id=item.id,
                    month=item.month,
                    year=item.year,
                    status=item.status,
                    created_by_name=item.created_by.full_name,
                    approved_by_name=None
                    if item.approved_by is None
                    else item.approved_by.full_name,
                )
                for item in items
            ]

        return await paginate(
            db, query, params=Params(page=page, size=size), transformer=items_transformer
        )

    async def get_cycle_by_id(self, db: AsyncSession, id: int) -> PayrollCycle:
        result = await db.execute(
            select(PayrollCycle)
            .options(joinedload(PayrollCycle.created_by), joinedload(PayrollCycle.approved_by))
            .where(PayrollCycle.id == id)
        )
        return result.scalar_one()

    async def cycle_already_exists(self, db: AsyncSession, month: int, year: int) -> bool:
        count_result = await db.execute(
            select(func.count())
            .select_from(PayrollCycle)
            .where(
                and_(
                    PayrollCycle.month == month,
                    PayrollCycle.year == year,
                )
            )
        )

        return count_result.scalar_one() != 0

    async def generate_cycle(
        self,
        db: AsyncSession,
        month: int,
        year: int,
        current_user_id: int,
    ) -> None:
        cycle = PayrollCycle(
            month=month,
            year=year,
            created_by_id=current_user_id,
        )

        db.add(cycle)
        await db.flush([cycle])

        contracts = await contracts_crud.get_active(db, date=datetime.date(year, month, 28))
        for contract in contracts:
            db.add(
                PayrollRecord(
                    cycle_id=cycle.id,
                    employee_id=contract.employee_id,
                    base_salary=contract.base_salary,
                    allowance=contract.allowance,
                )
            )

        await db.commit()

    async def edit_cycle(
        self, db: AsyncSession, current_user: User, cycle_id: int, cycle_status: PayrollCycleStatus
    ) -> None:
        cycle_result = await db.execute(select(PayrollCycle).where(PayrollCycle.id == cycle_id))
        cycle = cycle_result.scalar_one()

        # Only the PAYROLL_CYCLES_APPROVE can edit the status to or from APPROVED and PAID
        permission_locked_statuses = (PayrollCycleStatus.APPROVED, PayrollCycleStatus.PAID)
        if cycle_status in permission_locked_statuses or cycle.status in permission_locked_statuses:
            permission_code = PermissionCode.PAYROLL_CYCLES_APPROVE
            permissions = await get_user_permissions(db, current_user)
            generic_permission_code = generate_generic_permission(permission_code)

            if permission_code not in permissions and generic_permission_code not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User lacks required permission: {permission_code}",
                )

        cycle.status = cycle_status
        if cycle.status == PayrollCycleStatus.APPROVED:
            cycle.approved_by_id = current_user.id

        db.add(cycle)

    async def delete_cycle(self, db: AsyncSession, id: int) -> None:
        await db.execute(delete(PayrollRecord).where(PayrollRecord.cycle_id == id))
        await db.execute(delete(PayrollCycle).where(PayrollCycle.id == id))

    async def get_cycle_records(
        self,
        db: AsyncSession,
        cycle_id: int,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        page: int = 1,
        size: int = 100,
    ) -> PayrollRecordGetDataPage:
        query = (
            select(PayrollRecord)
            .join(PayrollCycle, PayrollCycle.id == PayrollRecord.cycle_id)
            .join(User, User.id == PayrollRecord.employee_id)
            .join(Role, Role.id == User.role_id)
            .where(PayrollCycle.id == cycle_id)
            .options(
                joinedload(PayrollRecord.employee).joinedload(User.role),
                joinedload(PayrollRecord.cycle),
            )
        )

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(User.full_name.ilike(search_term), Role.name_ar.ilike(search_term))
            )

        sort_columns = {
            "id": PayrollRecord.id,
            "employee_name": User.full_name,
            "role_name_ar": Role.name_ar,
            "base_salary": PayrollRecord.base_salary,
            "allowance": PayrollRecord.allowance,
            "bonuses": PayrollRecord.bonuses,
            "deductions": PayrollRecord.deductions,
        }

        sort_column = sort_columns.get(sort_by, PayrollRecord.id)
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        async def items_transformer(
            items: Sequence[PayrollRecord],
        ) -> Sequence[PayrollRecordGetData]:
            return [
                PayrollRecordGetData(
                    id=item.id,
                    employee_name=item.employee.full_name,
                    role_name_ar=None if item.employee.role is None else item.employee.role.name_ar,
                    base_salary=str(item.base_salary),
                    allowance=str(item.allowance),
                    bonuses=str(item.bonuses),
                    deductions=str(item.deductions),
                    total=str(item.base_salary + item.allowance + item.bonuses - item.deductions),
                )
                for item in items
            ]

        total_query_result = await db.execute(
            select(
                func.sum(
                    PayrollRecord.base_salary
                    + PayrollRecord.allowance
                    + PayrollRecord.bonuses
                    - PayrollRecord.deductions
                )
            )
            .select_from(PayrollRecord)
            .where(PayrollRecord.cycle_id == cycle_id)
        )
        total = total_query_result.scalar_one()
        return PayrollRecordGetDataPage(
            items_total=str(total),
            page_info=await paginate(
                db,
                query,
                params=Params(page=page, size=size),
                transformer=items_transformer,
            ),
        )

    async def get_cycle_record_by_id(self, db: AsyncSession, id: int) -> PayrollRecord | None:
        return (await db.execute(select(PayrollRecord).where(PayrollRecord.id == id))).scalar()

    async def edit_cycle_record(
        self,
        db: AsyncSession,
        record: PayrollRecord,
        data: PayrollRecordEditData,
    ) -> None:
        for field in ("bonuses", "deductions"):
            value = getattr(data, field, None)
            if value:
                setattr(record, field, Decimal(value))

        db.add(record)


payroll_cycles_crud = PayrollCyclesCrud()
