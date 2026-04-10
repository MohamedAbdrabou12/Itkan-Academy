import json
from pathlib import Path

from app.modules.roles.models import Role
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_roles(db: AsyncSession) -> None:
    print("Seeding roles...")
    roles_file = current_dir / "roles.json"
    with Path.open(roles_file) as file:
        roles_data = json.load(file)

    roles_to_add = []
    for role_data in roles_data:
        result = await db.execute(select(Role).where(Role.id == role_data["id"]))
        existing_role = result.scalars().first()

        if not existing_role:
            roles_to_add.append(Role(**role_data))
            print(f"  - Preparing to add Roles data {role_data['name']}")
        else:
            # Role exists, check if it needs updating
            needs_update = False
            update_fields = []

            for key, value in role_data.items():
                if key != "id" and hasattr(existing_role, key):
                    current_value = getattr(existing_role, key)
                    if current_value != value:
                        setattr(existing_role, key, value)
                        needs_update = True
                        update_fields.append(key)

            if needs_update:
                # Merge the existing role to mark it as modified
                db.add(existing_role)
                print(f"  ↻ Updating role: {existing_role.name} (ID: {existing_role.id})")
                print(f"    Changed fields: {', '.join(update_fields)}")
            else:
                print(
                    f"  ○ Role already up-to-date: {existing_role.name} (ID: {existing_role.id})"
                )

            print(f"  - Roles data {role_data['name']} already exists, skipping.")

    if roles_to_add:
        db.add_all(roles_to_add)
        print(f"  - Adding {len(roles_to_add)} new roles to the session.")
    else:
        print("  - No new roles to add.")
