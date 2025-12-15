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

    for student_data in students_data:
        student_id = student_data["id"]
        user_id = student_data.get("user_id", "Unknown")

        # Check if student exists
        result = await db.execute(select(Student).where(Student.id == student_id))
        existing_student = result.scalars().first()

        # Pre-process date fields
        if "admission_date" in student_data and student_data["admission_date"]:
            student_data["admission_date"] = datetime.strptime(
                student_data["admission_date"], "%Y-%m-%d"
            ).date()

        if not existing_student:
            # Student doesn't exist, add it
            student = Student(**student_data)
            db.add(student)
            print(f"  ✓ Adding new student: ID {student_id} (User ID: {user_id})")
        else:
            # Student exists, check if it needs updating
            needs_update = False
            update_fields = []

            for key, value in student_data.items():
                if key != "id" and hasattr(existing_student, key):
                    current_value = getattr(existing_student, key)

                    # Special handling for date comparison
                    if key == "admission_date":
                        continue
                    else:
                        if current_value != value:
                            setattr(existing_student, key, value)
                            needs_update = True
                            update_fields.append(key)

            if needs_update:
                db.add(existing_student)
                print(f"  ↻ Updating student: ID {student_id} (User ID: {user_id})")
                if update_fields:
                    print(f"    Changed fields: {', '.join(update_fields)}")
            else:
                print(
                    f"  ○ Student already up-to-date: ID {student_id} (User ID: {user_id})"
                )
                
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"  ✗ Error seeding students: {e}")
        raise
