from typing import Optional, Dict, List
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.parents.crud import parent_crud
from app.modules.parents.models import Parent
from app.modules.students.crud import student_crud
from app.modules.users.crud import user_crud
from app.modules.roles.models import Role
from app.modules.users.models import UserStatus


class ParentService:
    @staticmethod
    async def _parent_branch_ids(parent: Parent) -> List[int]:
        branches = set()
        for child in getattr(parent, "children", []) or []:
            for b in getattr(child, "branch_ids", []) or []:
                branches.add(b)
        return list(branches)

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
            db,
            page=page,
            size=size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
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
        return await parent_crud.get_by_id(db, parent_id)

    @staticmethod
    async def create_parent(
        db: AsyncSession, payload: dict, creator: Optional[dict] = None
    ) -> Dict:
        if await user_crud.get_by_email(db, payload["email"]):
            raise HTTPException(status_code=400, detail="Email already registered")
        role = (
            await db.execute(select(Role).where(Role.name.ilike("parent")))
        ).scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=400, detail="Role 'parent' not found")
        payload["role_id"] = role.id
        return await parent_crud.create(db, payload)

    @staticmethod
    async def update_parent(db: AsyncSession, parent_id: int, payload: dict) -> Dict:
        parent_obj = await db.get(Parent, parent_id)
        if not parent_obj:
            raise HTTPException(status_code=404, detail="Parent not found")
        if "email" in payload:
            existing = await user_crud.get_by_email(db, payload["email"])
            if existing and existing.id != parent_obj.user_id:
                raise HTTPException(status_code=400, detail="Email already registered")
        return await parent_crud.update(db, parent_obj, payload)

    @staticmethod
    async def delete_parent(db: AsyncSession, parent_id: int) -> Dict:
        parent_obj = await parent_crud.get_by_id(db, parent_id)
        for child in parent_obj.get("children", []):
            if child.get("status") != UserStatus.deactive.value:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot deactivate parent with active children",
                )
        return await parent_crud.delete(db, parent_id)

    @staticmethod
    async def link_child(
        db: AsyncSession,
        parent_id: int,
        student_id: int,
        request: Optional[Request] = None,
    ) -> Dict:
        parent = await db.get(Parent, parent_id)
        student = await student_crud.get_by_id(db, student_id)
        if not parent or not student:
            raise HTTPException(status_code=404, detail="Not found")

        active_branch = (
            getattr(request.state, "active_branch_id", None) if request else None
        )
        if active_branch and active_branch not in getattr(student, "branch_ids", []):
            raise HTTPException(status_code=400, detail="Student not in branch")

        await parent_crud.link_child(db, parent, student)
        parent_user = await db.get(type(parent.user), parent.user_id)
        merged = list(
            set([link.branch_id for link in getattr(parent_user, "branch_links", [])])
            | set(getattr(student, "branch_ids", []) or [])
        )
        await user_crud.assign_branches(db, parent_user, merged)
        return await parent_crud.get_by_id(db, parent_id)

    @staticmethod
    async def unlink_child(db: AsyncSession, parent_id: int, student_id: int) -> Dict:
        parent = await db.get(Parent, parent_id)
        student = await student_crud.get_by_id(db, student_id)
        if not parent or not student:
            raise HTTPException(status_code=404, detail="Not found")

        await parent_crud.unlink_child(db, parent, student)
        branch_ids = await ParentService._parent_branch_ids(parent)
        parent_user = await db.get(type(parent.user), parent.user_id)
        await user_crud.assign_branches(db, parent_user, branch_ids)
        return await parent_crud.get_by_id(db, parent_id)
