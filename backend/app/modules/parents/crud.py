from typing import List, Optional, Dict
from fastapi import HTTPException
from sqlalchemy import select, asc, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.modules.parents.models import Parent, ParentStudent
from app.modules.users.models import User
from app.modules.students.models import Student
from app.modules.users.crud import user_crud
from app.modules.users.schemas import BranchInfo


def map_parent_to_read(parent: Parent) -> Dict:
    user = getattr(parent, "user", None)
    user_data = None
    if user:
        user_branch_name = None
        if user.branches:
            user_branch_name = user.branches[0].name
        elif getattr(parent, "children", []):
            for child in parent.children:
                if child.user and child.user.branches:
                    user_branch_name = child.user.branches[0].name
                    break

        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role_id": user.role_id,
            "role_name": user.role_name,
            "role_name_ar": user.role_name_ar,
            "branch_name": user_branch_name,
            "status": user.status,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "branch_ids": parent.branch_ids,
            "branches": parent.branches,
        }

    children = []
    for c in getattr(parent, "children", []) or []:
        child_user = getattr(c, "user", None)
        child_user_data = None
        if child_user:
            child_user_data = {
                "id": child_user.id,
                "full_name": child_user.full_name,
                "email": child_user.email,
                "phone": child_user.phone,
                "role_id": child_user.role_id,
                "role_name": child_user.role_name,
                "branch_name": child_user.branch_name,
                "role_name_ar": child_user.role_name_ar,
                "class_ids": [link.class_id for link in c.class_links]
                if c.class_links
                else [],
                "status": child_user.status,
                "branch_ids": [link.branch_id for link in child_user.branch_links]
                if child_user.branch_links
                else [],
                "branches": [
                    BranchInfo.from_orm(link.branch).model_dump()
                    for link in child_user.branch_links
                ]
                if child_user.branch_links
                else [],
            }
        children.append(
            {
                **(child_user_data or {}),
                "student_id": c.id,
                "admission_date": c.admission_date,
                "curriculum_progress": getattr(c, "curriculum_progress", None),
                "created_at": getattr(c, "created_at", None),
                "updated_at": getattr(c, "updated_at", None),
                "last_login": getattr(child_user, "last_login", None),
            }
        )

    return {
        "id": parent.id,
        "occupation": parent.occupation,
        "address": parent.address,
        "relationship_type": parent.relationship_type,
        "user": user_data,
        "children": children,
        "created_at": parent.created_at,
        "updated_at": parent.updated_at,
    }


class ParentCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ) -> List[Parent]:
        # Return parents list (unpaginated here). Allows searching by user name/email/phone.
        stmt = select(Parent).options(
            selectinload(Parent.user).selectinload(User.branch_links),
            selectinload(Parent.children)
            .selectinload(Student.user)
            .selectinload(User.branch_links),
        )

        if search:
            term = f"%{search}%"
            stmt = stmt.join(Parent.user).where(
                or_(
                    User.full_name.ilike(term),
                    User.email.ilike(term),
                    User.phone.ilike(term),
                )
            )

        sort_columns = {
            "id": Parent.id,
            "created_at": Parent.created_at,
            "updated_at": Parent.updated_at,
            "full_name": User.full_name,
            "email": User.email,
        }
        sort_col = sort_columns.get(sort_by, Parent.id)
        if sort_order and sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_col))
        else:
            stmt = stmt.order_by(asc(sort_col))

        res = await db.execute(stmt)
        return res.scalars().unique().all()

    async def get_by_id(self, db: AsyncSession, parent_id: int) -> Optional[Parent]:
        stmt = (
            select(Parent)
            .where(Parent.id == parent_id)
            .options(
                selectinload(Parent.user).selectinload(User.branch_links),
                selectinload(Parent.children)
                .selectinload(Student.user)
                .selectinload(User.branch_links),
                selectinload(Parent.children).selectinload(Student.class_links),
                selectinload(Parent.children_links),
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    async def create(self, db: AsyncSession, payload: dict) -> Parent:
        # Create linked user (role will be assigned by service) and create Parent record.
        # Parent user should not receive branch_ids at creation.
        # build user payload
        user_data = {
            "full_name": payload["full_name"],
            "email": payload["email"],
            "phone": payload.get("phone"),
            "password": payload.get("password"),
            "role_id": payload.get("role_id"),
        }
        user = await user_crud.create(db, user_data)

        parent_obj = Parent(
            user_id=user.id,
            occupation=payload.get("occupation"),
            address=payload.get("address"),
            relationship_type=payload.get("relationship_type"),
        )
        db.add(parent_obj)
        await db.commit()
        await db.refresh(parent_obj)
        return await self.get_by_id(db, parent_obj.id)

    async def update(self, db: AsyncSession, parent: Parent, data: dict) -> Parent:
        """
        Update parent fields and optionally update linked user fields via user_crud.update.
        """
        user_fields = {}
        for k in ("full_name", "email", "phone", "password", "status"):
            if k in data:
                user_fields[k] = data.pop(k)

        for field, value in data.items():
            if hasattr(parent, field):
                setattr(parent, field, value)

        db.add(parent)
        await db.commit()
        await db.refresh(parent)

        if user_fields:
            user = await db.get(User, parent.user_id)
            await user_crud.update(db, user, user_fields)

        return await self.get_by_id(db, parent.id)

    async def delete(self, db: AsyncSession, parent_id: int) -> Optional[Parent]:
        """
        Soft delete: set linked user.status = deactive.
        """
        parent = await self.get_by_id(db, parent_id)
        if not parent:
            return None
        user = await db.get(User, parent.user_id)
        if not user:
            return None
        from app.modules.users.models import UserStatus as US

        user.status = US.deactive.value
        db.add(user)
        await db.commit()
        await db.refresh(parent)
        return parent

    async def link_child(
        self, db: AsyncSession, parent: Parent, student: Student
    ) -> ParentStudent:
        # prevent duplicate
        stmt = select(ParentStudent).where(
            ParentStudent.parent_id == parent.id, ParentStudent.student_id == student.id
        )
        res = await db.execute(stmt)
        if res.scalars().first():
            raise HTTPException(
                status_code=400, detail="Parent already linked to this student"
            )

        link = ParentStudent(parent_id=parent.id, student_id=student.id)
        db.add(link)
        await db.commit()
        await db.refresh(link)
        await db.refresh(parent)
        return link

    async def unlink_child(
        self, db: AsyncSession, parent: Parent, student: Student
    ) -> bool:
        stmt = select(ParentStudent).where(
            ParentStudent.parent_id == parent.id, ParentStudent.student_id == student.id
        )
        res = await db.execute(stmt)
        link = res.scalars().first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        await db.delete(link)
        await db.commit()
        await db.refresh(parent)
        return True


parent_crud = ParentCRUD()
