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

    for user_data in users_data:
        user_id = user_data["id"]
        user_email = user_data["email"]

        result = await db.execute(select(User).where(User.id == user_id))
        existing_user = result.scalars().first()

        if "password" in user_data:
            user_data["password_hash"] = get_password_hash(user_data["password"])
            # Remove plain password from data
            user_data.pop("password", None)
       
        if not existing_user:
            user = User(**user_data)
            db.add(user)
            print(f"  ✓ Adding new user: {user_email} (ID: {user_id})")
        else:
            # User exists, check if it needs updating
            needs_update = False
            update_fields = []

            for key, value in user_data.items():
                if key != "id" and hasattr(existing_user, key):
                    if key == "password_hash":
                        continue
                    else:
                        current_value = getattr(existing_user, key)
                        if current_value != value:
                            setattr(existing_user, key, value)
                            needs_update = True
                            update_fields.append(key)

            if needs_update:
                # Merge the existing user to mark it as modified
                db.add(existing_user)
                print(f"  ↻ Updating user: {user_email} (ID: {user_id})")
                if update_fields:
                    print(f"    Changed fields: {', '.join(update_fields)}")
            else:
                print(f"  ○ User already up-to-date: {user_email} (ID: {user_id})")

    try:
        # Commit all changes at once
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"  ✗ Error seeding users: {e}")
        raise
