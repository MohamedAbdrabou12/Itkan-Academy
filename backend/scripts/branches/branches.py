import json
from pathlib import Path

from app.modules.branches.models import Branch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_branches(db: AsyncSession):
    print("Seeding branches...")
    branches_file = current_dir / "branches.json"
    with open(branches_file, "r") as file:
        branches_data = json.load(file)

    branches_to_add = []
    for branch_data in branches_data:
        result = await db.execute(select(Branch).where(Branch.id == branch_data["id"]))

        if not result.scalars().first():
            branches_to_add.append(Branch(**branch_data))
            print(f"  - Preparing to add Branches data {branch_data['id']}")
        else:
            print(f"  - Branches data {branch_data['id']} already exists, skipping.")

    if branches_to_add:
        db.add_all(branches_to_add)
        print(f"  - Adding {len(branches_to_add)} new branches to the session.")
    else:
        print("  - No new branches to add.")
