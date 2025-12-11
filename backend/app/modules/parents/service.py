from typing import Optional, Dict, List
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.parents.crud import parent_crud, map_parent_to_read
from app.modules.parents.models import Parent
from app.modules.students.crud import student_crud
from app.modules.users.crud import user_crud
from app.modules.roles.models import Role
from app.modules.users.models import UserStatus


class ParentService:
    @staticmethod
    async def _parent_branch_ids(parent: Parent) -> List[int]:
        # Return union of branch ids from parent's children.
        branches = set()
        for child in getattr(parent, "children", []) or []:
            # Student has branch_ids property
            child_branch_ids = getattr(child, "branch_ids", []) or []
            for b in child_branch_ids:
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
        parents = await parent_crud.get_all(
            db, search=search, sort_by=sort_by, sort_order=sort_order
        )
        items = [map_parent_to_read(p) for p in parents]
        total = len(items)
        start = (page - 1) * size
        end = start + size
        return {
            "items": items[start:end],
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
        db: AsyncSession, payload: dict, creator: Optional[dict] = None
    ) -> Dict:
        """
        Create parent user (no branches) and Parent record.
        - ensure role 'parent' exists
        - ensure email not used
        """
        # check email uniqueness
        existing = await user_crud.get_by_email(db, payload["email"])
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # get role 'parent'
        role_stmt = select(Role).where(Role.name.ilike("parent"))
        role_res = await db.execute(role_stmt)
        role = role_res.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=400, detail="Role 'parent' not found")

        payload["role_id"] = role.id

        parent = await parent_crud.create(db, payload)
        return map_parent_to_read(parent)

    @staticmethod
    async def update_parent(db: AsyncSession, parent_id: int, payload: dict) -> Dict:
        parent = await parent_crud.get_by_id(db, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        # if email changed -> ensure uniqueness
        if "email" in payload:
            existing = await user_crud.get_by_email(db, payload["email"])
            if existing and existing.id != parent.user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        updated = await parent_crud.update(db, parent, payload)
        return map_parent_to_read(updated)

    @staticmethod
    async def delete_parent(db: AsyncSession, parent_id: int) -> Dict:
        # Soft delete parent -> ensure no active children
        parent = await parent_crud.get_by_id(db, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        # Check active children (students whose linked user.status != deactive)
        for child in getattr(parent, "children", []) or []:
            child_user = getattr(child, "user", None)
            if child_user and child_user.status != UserStatus.deactive.value:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot deactivate parent with active children",
                )

        deleted = await parent_crud.delete(db, parent_id)
        return map_parent_to_read(deleted)

    @staticmethod
    async def link_child(
        db: AsyncSession,
        parent_id: int,
        student_id: int,
        request: Optional[Request] = None,
    ) -> Dict:
        """
        Link child to parent:
        - validate parent exists
        - validate student exists
        - if request has active_branch -> student must belong to it
        - create ParentStudent link
        - ensure parent's user.branches updated dynamically to include all child's branches
        - return updated ParentRead
        """
        parent = await parent_crud.get_by_id(db, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # check current branch if present
        active_branch = None
        if request:
            active_branch = getattr(request.state, "active_branch_id", None)
        if active_branch is not None:
            if active_branch not in getattr(student, "branch_ids", []):
                raise HTTPException(
                    status_code=400, detail="Student does not belong to current branch"
                )

        # create link
        await parent_crud.link_child(db, parent, student)

        # dynamically ensure parent's user has branch link(s) for the child's branches
        parent_user = await db.get(type(parent.user), parent.user_id)
        # gather branch ids from student
        student_branch_ids = getattr(student, "branch_ids", []) or []
        if student_branch_ids:
            # call user_crud.assign_branches to sync (this replaces existing branches).
            # But we must *add* branches not wipe existing. So get existing branch_ids:
            existing_branch_ids = (
                [link.branch_id for link in parent_user.branch_links]
                if getattr(parent_user, "branch_links", None)
                else []
            )
            merged = list(set(existing_branch_ids) | set(student_branch_ids))
            await user_crud.assign_branches(db, parent_user, merged)

        # reload parent and return
        parent = await parent_crud.get_by_id(db, parent_id)
        return map_parent_to_read(parent)

    @staticmethod
    async def unlink_child(db: AsyncSession, parent_id: int, student_id: int) -> Dict:
        parent = await parent_crud.get_by_id(db, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        await parent_crud.unlink_child(db, parent, student)

        # after unlink, recalc parent's branches = union of remaining children
        parent = await parent_crud.get_by_id(db, parent_id)
        branch_ids = await ParentService._parent_branch_ids(parent)

        parent_user = await db.get(type(parent.user), parent.user_id)
        # If branch_ids empty -> remove all branches, else assign union
        await user_crud.assign_branches(db, parent_user, branch_ids)

        parent = await parent_crud.get_by_id(db, parent_id)
        return map_parent_to_read(parent)
