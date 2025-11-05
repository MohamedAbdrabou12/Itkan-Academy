import json
from pathlib import Path

from app.modules.roles.models import Role
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_roles(db: AsyncSession):
    print("Seeding roles...")
    roles_file = current_dir / "roles.json"
    with open(roles_file, "r") as file:
        roles_data = json.load(file)

    roles_to_add = []
    for role_data in roles_data:
        result = await db.execute(select(Role).where(Role.id == role_data["id"]))

        if not result.scalars().first():
            roles_to_add.append(Role(**role_data))
            print(f"  - Preparing to add Roles data {role_data['name']}")
        else:
            print(f"  - Roles data {role_data['name']} already exists, skipping.")

    if roles_to_add:
        db.add_all(roles_to_add)
        print(f"  - Adding {len(roles_to_add)} new roles to the session.")
    else:
        print("  - No new roles to add.")
