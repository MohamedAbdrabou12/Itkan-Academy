from typing import Optional, Dict
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.parents.crud import parent_crud, map_parent_to_read
from app.modules.students.crud import student_crud
from app.modules.users.crud import user_crud
from app.modules.roles.models import Role
from app.modules.users.models import User, UserStatus


class ParentService:
    @staticmethod
    async def list_parents(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ) -> Dict:
        items, total = await parent_crud.get_paginated(
            db, page, size, search, sort_by, sort_order
        )
        return {
            "items": items,
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
        }

    @staticmethod
    async def get_parent(db: AsyncSession, parent_id: int) -> Dict:
        parent = await parent_crud.get_by_id(db, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")
        return map_parent_to_read(parent)

    @staticmethod
    async def create_parent(
        db: AsyncSession,
        payload: dict,
        creator: Optional[User] = None,  # Add this to handle the argument from router
    ) -> Dict:
        if await user_crud.get_by_email(db, payload["email"]):
            raise HTTPException(status_code=400, detail="Email already registered")

        role_res = await db.execute(select(Role).where(Role.name.ilike("parent")))
        role = role_res.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=400, detail="Role 'parent' not found")

        payload["role_id"] = role.id
        parent_obj = await parent_crud.create(db, payload)

        # Fresh fetch with all relationships loaded for the response
        return await ParentService.get_parent(db, parent_obj.id)

    @staticmethod
    async def update_parent(db: AsyncSession, parent_id: int, payload: dict) -> Dict:
        parent_obj = await parent_crud.get_by_id(db, parent_id)
        if not parent_obj:
            raise HTTPException(status_code=404, detail="Parent not found")

        if "email" in payload:
            existing = await user_crud.get_by_email(db, payload["email"])
            if existing and existing.id != parent_obj.user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        await parent_crud.update(db, parent_obj, payload)
        return await ParentService.get_parent(db, parent_id)

    @staticmethod
    async def delete_parent(db: AsyncSession, parent_id: int) -> Dict:
        parent = await parent_crud.get_by_id(db, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        user = await db.get(User, parent.user_id)
        if user:
            user.status = UserStatus.deactive.value
            db.add(user)
            await db.commit()

        return await ParentService.get_parent(db, parent_id)

    @staticmethod
    async def link_child(
        db: AsyncSession,
        parent_id: int,
        student_id: int,
        request: Optional[Request] = None,
    ) -> Dict:
        parent = await parent_crud.get_by_id(db, parent_id)
        student = await student_crud.get_by_id(db, student_id)

        if not parent or not student:
            raise HTTPException(status_code=404, detail="Parent or Student not found")

        await parent_crud.link_child(db, parent.id, student.id)

        student_branch_ids = [link.branch_id for link in student.user.branch_links]
        parent_user = parent.user
        current_parent_branches = [link.branch_id for link in parent_user.branch_links]

        merged_branches = list(set(current_parent_branches) | set(student_branch_ids))
        await user_crud.assign_branches(db, parent_user, merged_branches)

        return await ParentService.get_parent(db, parent_id)

    @staticmethod
    async def unlink_child(db: AsyncSession, parent_id: int, student_id: int) -> Dict:
        parent = await parent_crud.get_by_id(db, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        await parent_crud.unlink_child(db, parent_id, student_id)
        db.expire_all()

        # Re-fetch parent to get clean state
        updated_parent = await parent_crud.get_by_id(db, parent_id)

        new_branch_ids = set()
        for child in updated_parent.children:
            for link in child.user.branch_links:
                new_branch_ids.add(link.branch_id)

        # Update parent's branches based on remaining children
        await user_crud.assign_branches(db, updated_parent.user, list(new_branch_ids))

        await db.commit()  # Save the new branch associations

        return await ParentService.get_parent(db, parent_id)
