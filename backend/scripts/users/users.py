import json
from pathlib import Path

from app.modules.users.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash


current_dir = Path(__file__).resolve().parent


async def add_users(db: AsyncSession):
    print("Seeding users...")
    users_file = current_dir / "users.json"
    with open(users_file, "r") as file:
        users_data = json.load(file)

    users_to_add = []
    for user_data in users_data:
        result = await db.execute(select(User).where(User.id == user_data["id"]))

        if not result.scalars().first():

            user_data["password_hash"] = get_password_hash(user_data["password_hash"])
            users_to_add.append(User(**user_data))
            print(f"  - Preparing to add Users data {user_data['email']}")
        else:
            print(f"  - Users data {user_data['full_name']} already exists, skipping.")

    if users_to_add:
        db.add_all(users_to_add)
        print(f"  - Adding {len(users_to_add)} new users to the session.")
    else:
        print("  - No new users to add.")
