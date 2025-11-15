import json
from pathlib import Path
from datetime import datetime

from app.modules.students.models import Student
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_students(db: AsyncSession):
    print("Seeding students...")
    students_file = current_dir / "students.json"
    with open(students_file, "r") as file:
        students_data = json.load(file)

    students_to_add = []
    for student_data in students_data:
        result = await db.execute(
            select(Student).where(Student.id == student_data["id"])
        )

        if not result.scalars().first():
            # Convert date string to Python date object
            if "admission_date" in student_data and student_data["admission_date"]:
                student_data["admission_date"] = datetime.strptime(
                    student_data["admission_date"], "%Y-%m-%d"
                ).date()

            students_to_add.append(Student(**student_data))
            print(
                f"  - Preparing to add Students data with user_id: {student_data['user_id']}"
            )
        else:
            print(
                f"  - Students data with user_id: {student_data['user_id']} already exists, skipping."
            )

    if students_to_add:
        db.add_all(students_to_add)
        print(f"  - Adding {len(students_to_add)} new students to the session.")
    else:
        print("  - No new students to add.")
