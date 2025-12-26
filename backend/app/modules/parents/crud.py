from typing import List, Optional, Dict
from sqlalchemy import select, asc, desc, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.modules.parents.models import Parent, ParentStudent
from app.modules.users.models import User, UserBranch
from app.modules.students.models import Student
from app.modules.users.crud import user_crud
from app.modules.users.schemas import BranchInfo


def map_parent_to_read(parent: Parent) -> Dict:
    user = getattr(parent, "user", None)
    user_data = None
    if user:
        branches = [
            link.branch for link in getattr(user, "branch_links", []) if link.branch
        ]
        user_branch_name = branches[0].name if branches else None

        if not user_branch_name and getattr(parent, "children", []):
            for child in parent.children:
                if child.user and child.user.branch_links:
                    first_link = child.user.branch_links[0]
                    if first_link.branch:
                        user_branch_name = first_link.branch.name
                        break

        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role_id": user.role_id,
            "role_name": getattr(user.role, "name", None),
            "role_name_ar": getattr(user.role, "name_ar", None),
            "branch_name": user_branch_name,
            "status": user.status,
            "login_type": user.login_type,
            "login_identifier": user.login_identifier,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "branch_ids": [b.id for b in branches],
            "branches": [BranchInfo.from_orm(b).model_dump() for b in branches],
        }

    children = []
    for c in getattr(parent, "children", []) or []:
        child_user = getattr(c, "user", None)
        child_user_data = None
        if child_user:
            child_branches = [
                link.branch
                for link in getattr(child_user, "branch_links", [])
                if link.branch
            ]
            child_user_data = {
                "id": child_user.id,
                "full_name": child_user.full_name,
                "email": child_user.email,
                "phone": child_user.phone,
                "role_id": child_user.role_id,
                "role_name": getattr(child_user.role, "name", None),
                "role_name_ar": getattr(child_user.role, "name_ar", None),
                "branch_name": child_branches[0].name if child_branches else None,
                "login_type": child_user.login_type,
                "login_identifier": child_user.login_identifier,
                "status": child_user.status,
                "class_ids": [cl.id for cl in getattr(c, "classes", [])],
                "branch_ids": [b.id for b in child_branches],
                "branches": [
                    BranchInfo.from_orm(b).model_dump() for b in child_branches
                ],
            }
        children.append(
            {
                **(child_user_data or {}),
                "student_id": c.id,
                "admission_date": c.admission_date,
                "national_id": c.national_id,
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
            joinedload(Parent.user).selectinload(User.role),
            joinedload(Parent.user)
            .selectinload(User.branch_links)
            .joinedload(UserBranch.branch),
            selectinload(Parent.children)
            .joinedload(Student.user)
            .selectinload(User.role),
            selectinload(Parent.children)
            .joinedload(Student.user)
            .selectinload(User.branch_links)
            .joinedload(UserBranch.branch),
            selectinload(Parent.children).selectinload(Student.classes),
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

        sort_columns = {"id": Parent.id, "created_at": Parent.created_at}
        sort_col = sort_columns.get(sort_by, Parent.id)
        stmt = stmt.order_by(desc(sort_col) if sort_order == "desc" else asc(sort_col))

        stmt = stmt.limit(size).offset((page - 1) * size)
        res = await db.execute(stmt)
        parents = res.scalars().unique().all()

        return [map_parent_to_read(p) for p in parents], total

    async def get_by_id(self, db: AsyncSession, parent_id: int) -> Optional[Parent]:
        stmt = (
            select(Parent)
            .where(Parent.id == parent_id)
            .options(
                joinedload(Parent.user).selectinload(User.role),
                joinedload(Parent.user)
                .selectinload(User.branch_links)
                .joinedload(UserBranch.branch),
                selectinload(Parent.children)
                .joinedload(Student.user)
                .selectinload(User.role),
                selectinload(Parent.children)
                .joinedload(Student.user)
                .selectinload(User.branch_links)
                .joinedload(UserBranch.branch),
                selectinload(Parent.children).selectinload(Student.classes),
                selectinload(Parent.children_links),
            )
        )
        res = await db.execute(stmt)
        return res.scalars().unique().first()

    async def create(self, db: AsyncSession, payload: dict) -> Parent:
        email_val = payload.get("email")
        user_data = {
            "full_name": payload.pop("full_name"),
            "email": payload.pop("email"),
            "phone": payload.pop("phone", None),
            "role_id": payload.pop("role_id"),
            "login_type": "email",
            "login_identifier": email_val,
            "password": None,
            # "password": payload.pop("password", None),
        }
        user = await user_crud.create(db, user_data)
        parent_obj = Parent(user_id=user.id, **payload)
        db.add(parent_obj)
        await db.commit()
        await db.refresh(parent_obj)
        return parent_obj

    async def update(self, db: AsyncSession, parent: Parent, data: dict) -> Parent:
        user_fields = {
            k: data.pop(k)
            for k in ("full_name", "email", "phone", "status")
            if k in data
        }

        for field, value in data.items():
            if hasattr(parent, field):
                setattr(parent, field, value)

        if user_fields:
            user = await db.get(User, parent.user_id)
            if user:
                for k, v in user_fields.items():
                    setattr(user, k, v)
                db.add(user)

        db.add(parent)
        await db.commit()
        await db.refresh(parent)
        return parent

    async def link_child(self, db: AsyncSession, parent_id: int, student_id: int):
        stmt = select(ParentStudent).where(
            ParentStudent.parent_id == parent_id, ParentStudent.student_id == student_id
        )
        existing = (await db.execute(stmt)).scalars().first()
        if not existing:
            db.add(ParentStudent(parent_id=parent_id, student_id=student_id))
            await db.commit()

    async def unlink_child(self, db: AsyncSession, parent_id: int, student_id: int):
        await db.execute(
            delete(ParentStudent).where(
                ParentStudent.parent_id == parent_id,
                ParentStudent.student_id == student_id,
            )
        )
        parent = await db.get(Parent, parent_id)
        if parent:
            db.expire(parent)

        await db.commit()


parent_crud = ParentCRUD()
