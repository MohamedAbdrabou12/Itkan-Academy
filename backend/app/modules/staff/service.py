# backend/app/modules/staff/service.py
from typing import List, Dict, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.staff.models import Staff
from app.modules.staff.schemas import StaffCreate, StaffUpdate
from app.modules.staff.crud import staff_crud
from app.modules.users.models import User, UserStatus
from app.modules.users.schemas import (
    UserRead,
    UserCreate as UserCreateSchema,
    UserUpdate,
    BranchInfo,
)
from app.modules.users.crud import user_crud
from app.modules.roles.models import Role
from app.services.notification_service.workrs.worker import send_notification_task


class StaffService:
    @staticmethod
    async def _serialize_staff(staff: Staff) -> Dict:
        user: User = getattr(staff, "user", None)
        # Serialize user data like TeacherService
        user_data = UserRead(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role_id=user.role_id,
            role_name=user.role_name,
            branch_name=user.branch_name,
            permission_code=user.role.permission_links if user.role else None,
            status=user.status,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
            branch_ids=[link.branch_id for link in user.branch_links]
            if user.branch_links
            else None,
            branches=[BranchInfo.from_orm(link.branch) for link in user.branch_links]
            if user.branch_links
            else None,
        )

        return {
            **user_data.model_dump(),
            "position": staff.position,
            "salary_meta": staff.salary_meta,
        }

    @staticmethod
    async def list_staff(db: AsyncSession) -> List[Dict]:
        staff_list = await staff_crud.get_all(db)
        return [await StaffService._serialize_staff(s) for s in staff_list]

    @staticmethod
    async def get_staff(db: AsyncSession, staff_id: int) -> Dict:
        staff = await staff_crud.get_by_id(db, staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        if not staff.user:
            staff.user = await db.get(User, staff.user_id)
        return await StaffService._serialize_staff(staff)

    @staticmethod
    async def create_staff(
        db: AsyncSession, staff_in: StaffCreate, creator: Optional[User] = None
    ) -> Dict:
        existing = await user_crud.get_by_email(db, staff_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        if not staff_in.branch_ids or len(staff_in.branch_ids) == 0:
            raise HTTPException(
                status_code=400, detail="Staff must belong to at least one branch"
            )

        # enforce creator branch restriction
        if creator and getattr(creator, "role_name", "").lower() != "admin":
            if not all(
                bid in getattr(creator, "branch_ids", []) for bid in staff_in.branch_ids
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Staff branches must match creator's branches",
                )

        # Use role_id from payload instead of querying by name
        role_id = staff_in.role_id

        # create user
        primary_branch_id = staff_in.branch_ids[0]
        user_payload = UserCreateSchema(
            name=staff_in.name,
            email=staff_in.email,
            phone=staff_in.phone,
            role_id=role_id,
            branch_id=primary_branch_id,
            status=UserStatus.pending,
        )
        user = await user_crud.create(db, user_payload)

        if staff_in.branch_ids:
            await user_crud.assign_branches(db, user, staff_in.branch_ids)

        staff_payload = {
            "user_id": user.id,
            "position": staff_in.position,
            "salary_meta": staff_in.salary_meta,
        }
        staff = await staff_crud.create(db, staff_payload)

        await StaffService._notify_hr_new_staff(db, staff, creator)
        staff.user = user
        return await StaffService._serialize_staff(staff)

    @staticmethod
    async def update_staff(
        db: AsyncSession, staff_id: int, staff_in: StaffUpdate
    ) -> Dict:
        staff = await staff_crud.get_by_id(db, staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")

        user = await db.get(User, staff.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        data = staff_in.dict(exclude_unset=True)
        user_fields = {
            f: data.pop(f)
            for f in ("name", "email", "phone", "branch_ids")
            if f in data
        }
        if user_fields:
            if "email" in user_fields and user_fields["email"] != user.email:
                exist = await user_crud.get_by_email(db, user_fields["email"])
                if exist:
                    raise HTTPException(
                        status_code=400, detail="Email already registered"
                    )
            await user_crud.update(db, user, UserUpdate(**user_fields))
            if "branch_ids" in user_fields:
                await user_crud.assign_branches(db, user, user_fields["branch_ids"])

        if data:
            staff = await staff_crud.update(db, staff, data)

        staff.user = await db.get(User, staff.user_id)
        return await StaffService._serialize_staff(staff)

    @staticmethod
    async def delete_staff(db: AsyncSession, staff_id: int) -> Dict:
        staff = await staff_crud.get_by_id(db, staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        staff = await staff_crud.delete(db, staff)
        return await StaffService._serialize_staff(staff)

    @staticmethod
    async def approve_staff(
        db: AsyncSession, staff_id: int, approver: Optional[User] = None
    ) -> Dict:
        staff = await staff_crud.get_by_id(db, staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        staff = await staff_crud.approve(db, staff)

        payload = {
            "staff_id": staff.id,
            "staff_name": staff.user.name,
            "approved_by": approver.name if approver else "System",
        }
        try:
            send_notification_task.delay(
                user_id=str(staff.user.id),
                channel="web",
                template_type="staff_approved",
                payload=payload,
            )
        except Exception:
            pass
        return await StaffService._serialize_staff(staff)

    @staticmethod
    async def reject_staff(
        db: AsyncSession, staff_id: int, approver: Optional[User] = None
    ) -> Dict:
        staff = await staff_crud.get_by_id(db, staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        staff = await staff_crud.reject(db, staff)

        payload = {
            "staff_id": staff.id,
            "staff_name": staff.user.name,
            "rejected_by": approver.name if approver else "System",
        }
        try:
            send_notification_task.delay(
                user_id=str(staff.user.id),
                channel="web",
                template_type="staff_rejected",
                payload=payload,
            )
        except Exception:
            pass
        return await StaffService._serialize_staff(staff)

    @staticmethod
    async def _notify_hr_new_staff(
        db: AsyncSession, staff: Staff, creator: Optional[User] = None
    ):
        role_res = await db.execute(select(Role).where(Role.name.ilike("admin")))
        admin_role = role_res.scalar_one_or_none()
        if not admin_role:
            return

        res = await db.execute(select(User).where(User.role_id == admin_role.id))
        admins = res.scalars().all()
        if not admins:
            return

        payload = {
            "staff_id": staff.id,
            "staff_name": staff.user.name if staff.user else "Unknown",
            "created_by": creator.name if creator else "System",
        }
        for admin in admins:
            try:
                send_notification_task.delay(
                    user_id=str(admin.id),
                    channel="web",
                    template_type="new_staff_pending",
                    payload=payload,
                )
            except Exception:
                pass
