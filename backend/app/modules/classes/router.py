from fastapi import APIRouter, Depends, HTTPException, status
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
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await class_crud.get_all(db)


@class_router.get("/{class_id}", response_model=ClassRead)
async def get_class(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    class_ = await class_crud.get_by_id(db, class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_


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
    return await class_crud.create(db, class_in)


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
    return await class_crud.update(db, class_, class_in)


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
