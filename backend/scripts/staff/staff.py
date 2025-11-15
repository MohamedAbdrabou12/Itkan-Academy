import json
from pathlib import Path

from app.modules.staff.models import Staff
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_staff(db: AsyncSession):
    print("Seeding staff...")
    staff_file = current_dir / "staff.json"
    with open(staff_file, "r") as file:
        staff_data = json.load(file)

    staff_to_add = []
    for s_data in staff_data:
        result = await db.execute(select(Staff).where(Staff.id == s_data["id"]))

        if not result.scalars().first():
            staff_to_add.append(Staff(**s_data))
            print(f"  - Preparing to add Staff data with user_id: {s_data['user_id']}")
        else:
            print(
                f"  - Staff data with user_id: {s_data['user_id']} already exists, skipping."
            )

    if staff_to_add:
        db.add_all(staff_to_add)
        print(f"  - Adding {len(staff_to_add)} new staff to the session.")
    else:
        print("  - No new staff to add.")
