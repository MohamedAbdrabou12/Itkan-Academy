import json
from pathlib import Path

from app.modules.permissions.models import Permission
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_permissions(db: AsyncSession):
    print("Seeding permissions...")
    permissions_file = current_dir / "permissions.json"
    with open(permissions_file, "r") as file:
        permissions_data = json.load(file)

    permissions_to_add = []
    for permission_data in permissions_data:
        result = await db.execute(
            select(Permission).where(Permission.id == permission_data["id"])
        )

        if not result.scalars().first():
            permissions_to_add.append(Permission(**permission_data))
            print(f"  - Preparing to add Permissions data {permission_data['name']}")
        else:
            print(
                f"  - Permissions data {permission_data['name']} already exists, skipping."
            )

    if permissions_to_add:
        db.add_all(permissions_to_add)
        print(f"  - Adding {len(permissions_to_add)} new permissions to the session.")
    else:
        print("  - No new permissions to add.")
