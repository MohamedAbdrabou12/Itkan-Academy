# backend/app/modules/staff/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Request
from app.modules.staff.models import Staff
from app.modules.staff.schemas import StaffCreate, StaffUpdate
from app.core.utils import create_password_reset_token
from app.core.config import settings  # noqa
from app.services.notification_service.tasks.email import send_email_task
from app.services.notification_service.utils.template_engine import render_template


class StaffCRUD:
    async def get_all(
        self, db: AsyncSession, request: Optional[Request] = None
    ) -> List[Staff]:
        stmt = select(Staff).order_by(Staff.id)

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = stmt.where(Staff.branch_id == branch_id)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, staff_id: int, request: Optional[Request] = None
    ) -> Optional[Staff]:
        stmt = select(Staff).where(Staff.id == staff_id)

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = stmt.where(Staff.branch_id == branch_id)

        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, staff_in: StaffCreate) -> Staff:
        staff = Staff(**staff_in.dict())
        db.add(staff)
        await db.commit()
        await db.refresh(staff)

        # Generate reset password token
        token = create_password_reset_token(staff.user_id)
        # reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
        reset_link = f"https://www.google.com/search?q={token}"  # Temporary for testing
        # Render email template
        subject, body_html = render_template(
            "reset_password.html",
            {"username": staff.user.name, "reset_link": reset_link},
        )

        # Send email asynchronously via Celery
        send_email_task.delay(staff.user.email, subject, body_html)

        return staff

    async def update(
        self, db: AsyncSession, staff: Staff, staff_in: StaffUpdate
    ) -> Staff:
        data = staff_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(staff, field, value)
        db.add(staff)
        await db.commit()
        await db.refresh(staff)
        return staff

    async def delete(self, db: AsyncSession, staff_id: int) -> None:
        staff = await self.get_by_id(db, staff_id)
        if staff:
            await db.delete(staff)
            await db.commit()


staff_crud = StaffCRUD()
