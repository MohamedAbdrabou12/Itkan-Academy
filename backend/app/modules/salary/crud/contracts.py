import datetime
from collections.abc import Sequence
from decimal import Decimal

from app.modules.roles.models import Role
from app.modules.salary.models.contracts import Contract
from app.modules.salary.schemas.contracts import ContractEditData, ContractGetData
from app.modules.users.models import User, UserBranch
from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import and_, asc, delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ContractsCrud:
    async def get_all(
        self,
        db: AsyncSession,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        page: int = 1,
        size: int = 100,
    ) -> Page[ContractGetData]:
        query = (
            select(Contract)
            .join(User, User.id == Contract.employee_id)
            .join(Role, Role.id == User.role_id)
            .options(selectinload(Contract.employee).joinedload(User.role))
        )

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(User.full_name.ilike(search_term), Role.name_ar.ilike(search_term))
            )

        sort_columns = {
            "id": Contract.id,
            "employee_full_name": User.full_name,
            "role_name_ar": Role.name_ar,
            "base_salary": Contract.base_salary,
            "allowance": Contract.allowance,
            "effective_from": Contract.effective_from,
            "effective_to": Contract.effective_to,
            "created_at": Contract.created_at,
            "updated_at": Contract.updated_at,
        }

        sort_column = sort_columns.get(sort_by, Contract.id)
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        async def items_transformer(items: Sequence[Contract]) -> Sequence[ContractGetData]:
            return [
                ContractGetData(
                    id=item.id,
                    employee_id=item.employee_id,
                    employee_full_name=item.employee.full_name,
                    role_name_ar=None if item.employee.role is None else item.employee.role.name_ar,
                    base_salary=str(item.base_salary),
                    allowance=str(item.allowance),
                    effective_from=str(item.effective_from),
                    effective_to=str(item.effective_to),
                    created_at=item.created_at.isoformat(),
                    updated_at=item.updated_at.isoformat(),
                )
                for item in items
            ]

        return await paginate(
            db, query, params=Params(page=page, size=size), transformer=items_transformer
        )

    async def get_by_id(self, db: AsyncSession, id: int) -> Contract | None:
        return (await db.execute(select(Contract).where(Contract.id == id))).scalar()

    async def get_by_employee_id(self, db: AsyncSession, employee_id: int) -> Contract | None:
        date = datetime.datetime.now(datetime.timezone.utc).date()

        query = select(Contract).where(
            and_(
                Contract.employee_id == employee_id,
                Contract.effective_from < date,
                Contract.effective_to > date,
            )
        )

        result = await db.execute(query)
        return result.scalar()

    async def get_active(
        self,
        db: AsyncSession,
        branch_id: int | None = None,
        date: datetime.date | None = None,
    ) -> Sequence[Contract]:
        if date is None:
            date = datetime.datetime.now(datetime.timezone.utc).date()

        query = select(Contract).where(
            and_(Contract.effective_from <= date, Contract.effective_to >= date)
        )

        if branch_id is not None:
            query = (
                query.join(User, Contract.employee_id == User.id)
                .join(UserBranch, UserBranch.user_id == User.id)
                .where(UserBranch.branch_id == branch_id)
            )

        result = await db.execute(query)
        return result.scalars().all()

    async def active_contract_already_exists(self, db: AsyncSession, contract: Contract) -> bool:
        query_result = await db.execute(
            select(func.count())
            .select_from(Contract)
            .where(
                and_(
                    Contract.employee_id == contract.employee_id,
                    Contract.effective_from <= contract.effective_to,
                    Contract.effective_to >= contract.effective_from,
                )
            )
        )

        active_contract_count = query_result.scalar_one()
        return active_contract_count != 0

    async def register(
        self,
        db: AsyncSession,
        contract: Contract,
    ) -> None:
        db.add(contract)

    async def edit(self, db: AsyncSession, contract: Contract, data: ContractEditData) -> Contract:
        if data.employee_id is not None:
            contract.employee_id = data.employee_id

        for field in ("base_salary", "allowance"):
            value = getattr(data, field, None)
            if value:
                setattr(contract, field, Decimal(value))

        for field in ("effective_from", "effective_to"):
            value = getattr(data, field, None)
            if value:
                setattr(contract, field, datetime.date.fromisoformat(value))

        if contract.effective_to <= contract.effective_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="العقد مفعل إلى وقت قبل بداية التفعيل",
            )

        db.add(contract)
        return contract

    async def delete(self, db: AsyncSession, id: int) -> None:
        await db.execute(delete(Contract).where(Contract.id == id))
        await db.commit()


contracts_crud = ContractsCrud()
