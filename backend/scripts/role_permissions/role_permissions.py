import json
from pathlib import Path

from app.modules.role_permissions.models import RolePermission
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_role_permissions(db: AsyncSession):
    print("Seeding role_permissions...")
    role_permissions_file = current_dir / "role_permissions.json"
    with open(role_permissions_file, "r") as file:
        role_permissions_data = json.load(file)

    role_permissions_to_add = []
    for role_permission_data in role_permissions_data:
        result = await db.execute(
            select(RolePermission)
            .where(RolePermission.role_id == role_permission_data["role_id"])
            .where(
                RolePermission.permission_id == role_permission_data["permission_id"]
            )
        )

        if not result.scalars().first():
            role_permissions_to_add.append(RolePermission(**role_permission_data))
            print(
                f"  - Preparing to add RolePermissions data between role: {role_permission_data['role_id']} and permission: {role_permission_data['permission_id']}"
            )
        else:
            print(
                f"  - RolePermissions data between role: {role_permission_data['role_id']} and permission: {role_permission_data['permission_id']} already exists, skipping."
            )

    if role_permissions_to_add:
        db.add_all(role_permissions_to_add)
        print(
            f"  - Adding {len(role_permissions_to_add)} new role_permissions to the session."
        )
    else:
        print("  - No new role_permissions to add.")
