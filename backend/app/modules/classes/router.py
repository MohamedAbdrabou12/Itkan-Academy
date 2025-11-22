# backend/app/modules/classes/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.classes.schemas import ClassCreate, ClassRead, ClassUpdate
from app.modules.classes.crud import class_crud

class_router = APIRouter(prefix="/classes", tags=["Classes"])


@class_router.get("/", response_model=List[ClassRead])
async def list_classes(
    branch_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    classes = await class_crud.get_all(db, branch_id=branch_id)
    return [ClassRead.from_orm(c) for c in classes]


@class_router.get("/by-branch/{branch_id}", response_model=List[ClassRead])
async def get_classes_by_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
):
    classes = await class_crud.get_all(db, branch_id=branch_id)
    if not classes:
        raise HTTPException(status_code=404, detail="No classes found for this branch")
    return [ClassRead.from_orm(c) for c in classes]


@class_router.get("/{class_id}", response_model=ClassRead)
async def get_class(class_id: int, db: AsyncSession = Depends(get_db)):
    class_ = await class_crud.get_by_id(db, class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassRead.from_orm(class_)


@class_router.post(
    "/",
    response_model=ClassRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("class:create")),
    ],
)
async def create_class(class_in: ClassCreate, db: AsyncSession = Depends(get_db)):
    class_ = await class_crud.create(db, class_in)
    return ClassRead.from_orm(class_)


@class_router.put(
    "/{class_id}",
    response_model=ClassRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("class:update")),
    ],
)
async def update_class(
    class_id: int, class_in: ClassUpdate, db: AsyncSession = Depends(get_db)
):
    class_ = await class_crud.get_by_id(db, class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    updated_class = await class_crud.update(db, class_, class_in)
    return ClassRead.from_orm(updated_class)


@class_router.delete(
    "/{class_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("class:delete")),
    ],
)
async def delete_class(class_id: int, db: AsyncSession = Depends(get_db)):
    await class_crud.delete(db, class_id)
    return None
