from datetime import datetime
import json
from pathlib import Path

from app.modules.teachers.models import Teacher
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_teachers(db: AsyncSession):
    print("Seeding teachers...")
    teachers_file = current_dir / "teachers.json"
    with open(teachers_file, "r") as file:
        teachers_data = json.load(file)

    teachers_to_add = []
    for teacher_data in teachers_data:
        result = await db.execute(
            select(Teacher).where(Teacher.id == teacher_data["id"])
        )

        if not result.scalars().first():
            # Convert date string to Python date object
            if "hire_date" in teacher_data and teacher_data["hire_date"]:
                teacher_data["hire_date"] = datetime.strptime(
                    teacher_data["hire_date"], "%Y-%m-%d"
                ).date()
            teachers_to_add.append(Teacher(**teacher_data))
            print(
                f"  - Preparing to add Teachers data with user_id: {teacher_data['user_id']}"
            )
        else:
            print(
                f"  - Teachers data with user_id: {teacher_data['user_id']} already exists, skipping."
            )

    if teachers_to_add:
        db.add_all(teachers_to_add)
        print(f"  - Adding {len(teachers_to_add)} new teachers to the session.")
    else:
        print("  - No new teachers to add.")
