from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import List, Optional
from datetime import datetime

from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import NotificationCreate, NotificationUpdate


class NotificationCRUD:
    async def get_all(self, db: AsyncSession) -> List[Notification]:
        result = await db.execute(
            select(Notification).order_by(Notification.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, notification_id: int
    ) -> Optional[Notification]:
        return await db.get(Notification, notification_id)

    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[Notification]:
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, notif_in: NotificationCreate
    ) -> Notification:
        notif = Notification(**notif_in.dict())
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return notif

    async def update(
        self, db: AsyncSession, notif: Notification, notif_in: NotificationUpdate
    ) -> Notification:
        for field, value in notif_in.dict(exclude_unset=True).items():
            setattr(notif, field, value)
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return notif

    async def mark_as_sent(
        self, db: AsyncSession, notif_id: int
    ) -> Optional[Notification]:
        notif = await self.get_by_id(db, notif_id)
        if notif:
            notif.status = "sent"
            notif.sent_at = datetime.utcnow()
            db.add(notif)
            await db.commit()
            await db.refresh(notif)
        return notif

    async def delete(self, db: AsyncSession, notif_id: int) -> None:
        notif = await self.get_by_id(db, notif_id)
        if notif:
            await db.delete(notif)
            await db.commit()


notification_crud = NotificationCRUD()
