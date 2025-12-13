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

    for permission_data in permissions_data:
        permission_id = permission_data["id"]
        permission_name = permission_data["name"]

        # Check if permission exists
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        existing_permission = result.scalars().first()

        if not existing_permission:
            # Permission doesn't exist, add it
            permission = Permission(**permission_data)
            db.add(permission)
            print(f"  ✓ Adding new permission: {permission_name} (ID: {permission_id})")
        else:
            # Permission exists, check if it needs updating
            needs_update = False
            update_fields = []

            for key, value in permission_data.items():
                if key != "id" and hasattr(existing_permission, key):
                    current_value = getattr(existing_permission, key)
                    if current_value != value:
                        setattr(existing_permission, key, value)
                        needs_update = True
                        update_fields.append(key)

            if needs_update:
                # Merge the existing permission to mark it as modified
                db.add(existing_permission)
                print(
                    f"  ↻ Updating permission: {permission_name} (ID: {permission_id})"
                )
                print(f"    Changed fields: {', '.join(update_fields)}")
            else:
                print(
                    f"  ○ Permission already up-to-date: {permission_name} (ID: {permission_id})"
                )

    try:
        # Commit all changes at once
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"  ✗ Error seeding permissions: {e}")
        raise
