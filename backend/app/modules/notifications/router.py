from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime  # noqa: F401

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)
from app.modules.notifications.crud import notification_crud

notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])


# List all notifications (admin or hr)
@notification_router.get(
    "/",
    response_model=List[NotificationRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("notification:view")),
    ],
)
async def list_notifications(db: AsyncSession = Depends(get_db)):
    return await notification_crud.get_all(db)


# List user notifications (self)
@notification_router.get("/my", response_model=List[NotificationRead])
async def list_my_notifications(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await notification_crud.get_by_user(db, current_user.id)


# Get single notification
@notification_router.get(
    "/{notif_id}",
    response_model=NotificationRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("notification:view")),
    ],
)
async def get_notification(notif_id: int, db: AsyncSession = Depends(get_db)):
    notif = await notification_crud.get_by_id(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


# Create / push new notification
@notification_router.post(
    "/",
    response_model=NotificationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("notification:create")),
    ],
)
async def create_notification(
    notif_in: NotificationCreate, db: AsyncSession = Depends(get_db)
):
    notif = await notification_crud.create(db, notif_in)
    # Future: trigger actual push/email handler here
    return notif


# Update (mark as read/sent, etc.)
@notification_router.put(
    "/{notif_id}",
    response_model=NotificationRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("notification:update")),
    ],
)
async def update_notification(
    notif_id: int, notif_in: NotificationUpdate, db: AsyncSession = Depends(get_db)
):
    notif = await notification_crud.get_by_id(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return await notification_crud.update(db, notif, notif_in)


# Mark as sent (optional helper endpoint)
@notification_router.put(
    "/{notif_id}/mark-sent",
    response_model=NotificationRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("notification:update")),
    ],
)
async def mark_notification_sent(notif_id: int, db: AsyncSession = Depends(get_db)):
    notif = await notification_crud.mark_as_sent(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


# Delete notification
@notification_router.delete(
    "/{notif_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("notification:delete")),
    ],
)
async def delete_notification(notif_id: int, db: AsyncSession = Depends(get_db)):
    await notification_crud.delete(db, notif_id)
    return None
