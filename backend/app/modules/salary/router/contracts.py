from datetime import datetime
from decimal import Decimal
from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.permissions.permissions import PermissionCode
from app.modules.salary.crud.contracts import contracts_crud
from app.modules.salary.models.contracts import Contract
from app.modules.salary.schemas.contracts import (
    ContractEditData,
    ContractGetData,
    ContractRegisterData,
)
from app.modules.users.crud import user_crud
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

contracts_router = APIRouter(prefix="/contracts", tags=["Contracts"])


@contracts_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_CONTRACTS_VIEW))],
)
async def get_all_contracts(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Annotated[str | None, Query()] = None,
    sort_by: Annotated[str, Query()] = "id",
    sort_order: Annotated[str, Query()] = "asc",
    page: Annotated[int, Query()] = 1,
    size: Annotated[int, Query()] = 100,
) -> Page[ContractGetData]:
    return await contracts_crud.get_all(
        db, search=search, sort_by=sort_by, sort_order=sort_order, page=page, size=size
    )


@contracts_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_CONTRACTS_ADD))],
)
async def register_contract(
    data: ContractRegisterData,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    employee_id = data.employee_id

    employee = await user_crud.get_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User ID {employee_id} not found"
        )

    role_name = None if employee.role_name is None else employee.role_name.lower()
    if role_name in {"parent", "student"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot register contract for {role_name}",
        )

    base_salary = Decimal(data.base_salary)
    allowance = Decimal(data.allowance)

    effective_from = datetime.fromisoformat(data.effective_from)
    effective_to = datetime.fromisoformat(data.effective_to)

    if effective_to <= effective_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يجب أن يكون يوم نهاية تفعيل العقد بعد يوم بداية تفعيل العقد",
        )

    contract = Contract(
        employee_id=employee_id,
        base_salary=base_salary,
        allowance=allowance,
        effective_from=effective_from,
        effective_to=effective_to,
    )

    if await contracts_crud.active_contract_already_exists(db, contract):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="يوجد عقد مفعل للموظف")

    await contracts_crud.register(db, contract)
    await db.commit()


@contracts_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_CONTRACTS_EDIT))],
)
async def edit_contract(
    id: int, data: ContractEditData, db: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    contract = await contracts_crud.get_by_id(db, id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not find contract with id {id}"
        )

    contract = await contracts_crud.edit(db, contract, data)
    if contract.effective_to is not None and contract.effective_to <= contract.effective_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="العقد مفعل إلى وقت قبل بداية التفعيل",
        )

    if await contracts_crud.active_contract_already_exists(db, contract):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="يوجد عقد مفعل للموظف")

    await db.commit()


@contracts_router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_CONTRACTS_DELETE))],
)
async def delete_contract(id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    await contracts_crud.delete(db, id)
