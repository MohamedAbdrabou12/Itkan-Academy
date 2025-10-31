import asyncio
from app.core.security import get_password_hash
from app.modules.users.crud import user_crud
from app.db.session import AsyncSessionLocal


# Script to fix password hashes for all users in the database exceeding bcrypt limit
async def fix_all_passwords():
    async with AsyncSessionLocal() as db:
        users = await user_crud.get_all(db)
        updated_count = 0

        for u in users:
            # Check if the password hash needs to be fixed
            if not u.password_hash.startswith("$2b$"):
                # Truncate the password hash to 72 bytes and re-hash
                safe_pass = u.password_hash.encode("utf-8")[:72].decode(
                    "utf-8", errors="ignore"
                )
                u.password_hash = get_password_hash(safe_pass)
                db.add(u)
                updated_count += 1

        await db.commit()
        print(f"Updated {updated_count} users' passwords.")


if __name__ == "__main__":
    asyncio.run(fix_all_passwords())
