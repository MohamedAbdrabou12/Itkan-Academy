import json
from pathlib import Path
from app.modules.parents.models import Parent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_parents(db: AsyncSession):
    print("Seeding parents...")
    parents_file = current_dir / "parents.json"
    with open(parents_file, "r") as file:
        parents_data = json.load(file)

    parents_to_add = []
    for parent_data in parents_data:
        result = await db.execute(select(Parent).where(Parent.id == parent_data["id"]))

        if not result.scalars().first():
            parents_to_add.append(Parent(**parent_data))
            print(f"  - Preparing to add Parent with user_id: {parent_data['user_id']}")
        else:
            print(
                f"  - Parent with user_id: {parent_data['user_id']} already exists, skipping."
            )

    if parents_to_add:
        db.add_all(parents_to_add)
        print(f"  - Adding {len(parents_to_add)} new parents to the session.")
    else:
        print("  - No new parents to add.")
