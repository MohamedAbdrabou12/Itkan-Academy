from typing import List, Optional, Dict
from fastapi import HTTPException
from sqlalchemy import select, asc, desc, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.modules.parents.models import Parent, ParentStudent
from app.modules.users.models import User, UserBranch
from app.modules.students.models import Student
from app.modules.users.crud import user_crud
from app.modules.users.schemas import BranchInfo


def map_parent_to_read(parent: Parent) -> Dict:
    user = getattr(parent, "user", None)
    user_data = None
    if user:
        user_branch_name = user.branches[0].name if user.branches else None
        if not user_branch_name and getattr(parent, "children", []):
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
            "login_type": user.login_type,
            "login_identifier": user.login_identifier,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "branch_ids": [b.id for b in user.branches] if user.branches else [],
            "branches": [BranchInfo.from_orm(b).model_dump() for b in user.branches]
            if user.branches
            else [],
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
                "login_type": child_user.login_type,
                "login_identifier": child_user.login_identifier,
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
    async def get_paginated(
        self,
        db: AsyncSession,
        page: int,
        size: int,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ) -> tuple[List[Dict], int]:
        stmt = select(Parent).options(
            selectinload(Parent.user)
            .selectinload(User.branch_links)
            .selectinload(UserBranch.branch),
            selectinload(Parent.children)
            .selectinload(Student.user)
            .selectinload(User.branch_links)
            .selectinload(UserBranch.branch),
            selectinload(Parent.children).selectinload(Student.class_links),
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

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        sort_columns = {
            "id": Parent.id,
            "created_at": Parent.created_at,
            "full_name": User.full_name,
        }
        sort_col = sort_columns.get(sort_by, Parent.id)
        stmt = stmt.order_by(desc(sort_col) if sort_order == "desc" else asc(sort_col))

        stmt = stmt.limit(size).offset((page - 1) * size)
        res = await db.execute(stmt)
        parents = res.scalars().unique().all()

        return [map_parent_to_read(p) for p in parents], total

    async def get_by_id(self, db: AsyncSession, parent_id: int) -> Dict:
        stmt = (
            select(Parent)
            .where(Parent.id == parent_id)
            .options(
                selectinload(Parent.user)
                .selectinload(User.branch_links)
                .selectinload(UserBranch.branch),
                selectinload(Parent.children)
                .selectinload(Student.user)
                .selectinload(User.branch_links)
                .selectinload(UserBranch.branch),
                selectinload(Parent.children).selectinload(Student.class_links),
                selectinload(Parent.children_links),
            )
        )
        res = await db.execute(stmt)
        parent = res.scalars().first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")
        return map_parent_to_read(parent)

    async def create(self, db: AsyncSession, payload: dict) -> Dict:
        user_data = {
            "full_name": payload["full_name"],
            "email": payload["email"],
            "phone": payload.get("phone"),
            "role_id": payload.get("role_id"),
            "login_type": "email",
            "login_identifier": payload["email"],
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
        return await self.get_by_id(db, parent_obj.id)

    async def update(self, db: AsyncSession, parent: Parent, data: dict) -> Dict:
        user_fields = {
            k: data.pop(k)
            for k in ("full_name", "email", "phone", "status")
            if k in data
        }
        for field, value in data.items():
            if hasattr(parent, field):
                setattr(parent, field, value)
        db.add(parent)
        if user_fields:
            user = await db.get(User, parent.user_id)
            await user_crud.update(db, user, user_fields)
        await db.commit()
        return await self.get_by_id(db, parent.id)

    async def delete(self, db: AsyncSession, parent_id: int) -> Dict:
        parent = await db.get(Parent, parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")
        user = await db.get(User, parent.user_id)
        from app.modules.users.models import UserStatus as US

        user.status = US.deactive.value
        db.add(user)
        await db.commit()
        return await self.get_by_id(db, parent.id)

    async def link_child(
        self, db: AsyncSession, parent: Parent, student: Student
    ) -> Dict:
        stmt = select(ParentStudent).where(
            ParentStudent.parent_id == parent.id, ParentStudent.student_id == student.id
        )
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=400, detail="Parent already linked")
        db.add(ParentStudent(parent_id=parent.id, student_id=student.id))
        await db.commit()
        return await self.get_by_id(db, parent.id)

    async def unlink_child(
        self, db: AsyncSession, parent: Parent, student: Student
    ) -> Dict:
        stmt = select(ParentStudent).where(
            ParentStudent.parent_id == parent.id, ParentStudent.student_id == student.id
        )
        link = (await db.execute(stmt)).scalars().first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        await db.delete(link)
        await db.commit()
        return await self.get_by_id(db, parent.id)


parent_crud = ParentCRUD()
