from typing import List, Optional

from app.modules.permissions.models import Permission
from app.modules.role_permissions.models import RolePermission
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class PermissionCRUD:
    async def get_role_permissions(
        self, db: AsyncSession, role_id: int
    ) -> List[RolePermission]:
        result = await db.execute(
            select(RolePermission)
            .filter(RolePermission.role_id == role_id)
            .options(selectinload(RolePermission.permission))
        )
        return list(result.scalars().all())

    async def get_all_permissions(self, db: AsyncSession) -> List[Permission]:
        result = await db.execute(select(Permission))
        return list(result.scalars().all())

    async def get_permission(
        self, db: AsyncSession, permission_id: int
    ) -> Optional[Permission]:
        result = await db.execute(
            select(Permission).filter(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_role_permission(
        self, db: AsyncSession, role_id: int, permission_id: int
    ) -> Optional[RolePermission]:
        result = await db.execute(
            select(RolePermission).filter(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def assign_permission_to_role(
        self, db: AsyncSession, role_id: int, permission_id: int
    ) -> RolePermission:
        # Check if assignment already exists
        existing = await self.get_role_permission(db, role_id, permission_id)
        if existing:
            return existing

        # Create new assignment
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        db.add(role_permission)
        return role_permission

    async def remove_permission_from_role(
        self, db: AsyncSession, role_id: int, permission_id: int
    ) -> bool:
        role_permission = await self.get_role_permission(db, role_id, permission_id)
        if role_permission:
            await db.delete(role_permission)
            return True
        return False

    async def sync_role_permissions(
        self, db: AsyncSession, role_id: int, permission_ids: List[int]
    ) -> List[RolePermission]:
        """
        Sync role permissions by adding new ones and removing ones not in the list
        This efficiently handles both adding and removing in a single operation
        """
        try:
            # Get current role permissions
            current_role_permissions = await self.get_role_permissions(db, role_id)
            current_permission_ids = {
                rp.permission_id for rp in current_role_permissions
            }
            new_permission_ids = set(permission_ids)

            # Permissions to add (in new list but not currently assigned)
            permissions_to_add = new_permission_ids - current_permission_ids

            # Permissions to remove (currently assigned but not in new list)
            permissions_to_remove = current_permission_ids - new_permission_ids

            # Validate that all permissions to add exist
            for permission_id in permissions_to_add:
                permission = await self.get_permission(db, permission_id)
                if not permission:
                    raise ValueError(
                        f"Permission with ID {permission_id} does not exist"
                    )

            # Add new permissions
            for permission_id in permissions_to_add:
                await self.assign_permission_to_role(db, role_id, permission_id)

            # Remove permissions that are no longer needed
            for permission_id in permissions_to_remove:
                await self.remove_permission_from_role(db, role_id, permission_id)

            # Commit all changes
            await db.commit()

            # Return updated role permissions
            return await self.get_role_permissions(db, role_id)

        except Exception as e:
            await db.rollback()
            raise e


permission_crud = PermissionCRUD()
