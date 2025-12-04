from typing import List, Optional
from app.modules.permissions.models import Permission
from app.modules.role_permissions.models import RolePermission
from app.modules.roles.models import Role
from app.modules.roles.schemas import RoleCreate, RoleUpdate
from fastapi import Request
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class RoleCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> dict:
        # Query with permissions_count using the hybrid property in the model
        query = select(Role).options(
            selectinload(Role.permission_associations).selectinload(
                RolePermission.permission
            )
        )

        # Apply search
        if search:
            search_filter = or_(
                Role.name.ilike(f"%{search}%"),
                Role.name_ar.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Apply sorting
        sort_column_name = sort_by or "id"
        sort_order_direction = sort_order or "asc"

        # Handle sorting for permissions_count
        if sort_column_name == "permissions_count":
            sort_column = Role.permissions_count
        else:
            sort_column = getattr(Role, sort_column_name, Role.name)

        query = query.order_by(
            sort_column.desc()
            if sort_order_direction.lower() == "desc"
            else sort_column.asc()
        )

        result = await sqlalchemy_paginate(db, query)
        return result

    async def get_by_id(
        self, db: AsyncSession, role_id: int, request: Optional[Request] = None
    ) -> Optional[Role]:
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(
                selectinload(Role.permission_associations).selectinload(
                    RolePermission.permission
                ),
                selectinload(Role.users),
            )
        )

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                # Roles are usually global; placeholder for future branch filtering
                pass

        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: RoleCreate) -> Role:
        # Extract permissions if provided
        permission_ids = getattr(obj_in, "permission_ids", [])

        # Create role
        db_obj = Role(
            name=obj_in.name,
            name_ar=obj_in.name_ar,
            description=obj_in.description,
            description_ar=obj_in.description_ar,
        )
        db.add(db_obj)
        await db.flush()  # Flush to get the ID

        # Add permissions if provided
        if permission_ids:
            await self._add_permissions_to_role(db, db_obj.id, permission_ids)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Role, obj_in: RoleUpdate) -> Role:
        data = obj_in.dict(exclude_unset=True)

        # Extract permission_ids if provided
        permission_ids = data.pop("permission_ids", None)

        # Update basic fields
        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # Update permissions if provided
        if permission_ids is not None:
            await self._update_role_permissions(db, db_obj.id, permission_ids)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, role_id: int) -> None:
        role = await self.get_by_id(db, role_id)
        if role:
            # The cascade="all, delete-orphan" will handle deleting role_permissions
            await db.delete(role)
            await db.commit()

    async def get_role_with_permissions(
        self, db: AsyncSession, role_id: int
    ) -> Optional[Role]:
        """Get role with permissions eagerly loaded"""
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(
                selectinload(Role.permission_associations).selectinload(
                    RolePermission.permission
                )
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def _add_permissions_to_role(
        self, db: AsyncSession, role_id: int, permission_ids: List[int]
    ) -> None:
        """Add permissions to a role"""
        for permission_id in permission_ids:
            # Check if permission exists
            permission_stmt = select(Permission).where(Permission.id == permission_id)
            permission_result = await db.execute(permission_stmt)
            permission = permission_result.scalar_one_or_none()

            if permission:
                # Check if association already exists
                existing_stmt = select(RolePermission).where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id,
                )
                existing_result = await db.execute(existing_stmt)
                existing = existing_result.scalar_one_or_none()

                if not existing:
                    role_permission = RolePermission(
                        role_id=role_id, permission_id=permission_id
                    )
                    db.add(role_permission)

    async def _update_role_permissions(
        self, db: AsyncSession, role_id: int, permission_ids: List[int]
    ) -> None:
        """Replace all permissions for a role with new set"""
        # Remove all existing permissions
        delete_stmt = select(RolePermission).where(RolePermission.role_id == role_id)
        delete_result = await db.execute(delete_stmt)
        existing_permissions = delete_result.scalars().all()

        for existing in existing_permissions:
            await db.delete(existing)

        # Add new permissions
        await self._add_permissions_to_role(db, role_id, permission_ids)

    async def get_role_permission_ids(
        self, db: AsyncSession, role_id: int
    ) -> List[int]:
        """Get list of permission IDs for a role"""
        stmt = select(RolePermission.permission_id).where(
            RolePermission.role_id == role_id
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def role_has_permission(
        self, db: AsyncSession, role_id: int, permission_code: str
    ) -> bool:
        """Check if a role has a specific permission by code"""
        stmt = (
            select(RolePermission)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id == role_id, Permission.code == permission_code
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_roles_by_permission(
        self, db: AsyncSession, permission_code: str
    ) -> List[Role]:
        """Get all roles that have a specific permission"""
        stmt = (
            select(Role)
            .join(RolePermission, Role.id == RolePermission.role_id)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(Permission.code == permission_code)
            .options(
                selectinload(Role.permission_associations).selectinload(
                    RolePermission.permission
                )
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


role_crud = RoleCRUD()
