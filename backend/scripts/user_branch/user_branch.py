import json
from pathlib import Path

from app.modules.users.models import UserBranch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_user_branch(db: AsyncSession):
    print("Seeding user_branch...")
    user_branch_file = current_dir / "user_branch.json"
    with open(user_branch_file, "r") as file:
        users_branches_data = json.load(file)

    user_branch_to_add = []
    for user_branch_data in users_branches_data:
        result = await db.execute(
            select(UserBranch)
            .where(UserBranch.user_id == user_branch_data["user_id"])
            .where(UserBranch.branch_id == user_branch_data["branch_id"])
        )

        if not result.scalars().first():
            user_branch_to_add.append(UserBranch(**user_branch_data))
            print(
                f"  - Preparing to add user_branch data between user: {user_branch_data['user_id']} and branch: {user_branch_data['branch_id']}"
            )
        else:
            print(
                f"  - user_branch data between user: {user_branch_data['user_id']} and branch: {user_branch_data['branch_id']} already exists, skipping."
            )

    if user_branch_to_add:
        db.add_all(user_branch_to_add)
        print(f"  - Adding {len(user_branch_to_add)} new user_branch to the session.")
    else:
        print("  - No new user_branch to add.")
