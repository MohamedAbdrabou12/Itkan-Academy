import json
from pathlib import Path
from datetime import datetime

from app.modules.students.models import StudentClass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_students_classes(db: AsyncSession):
    print("Seeding students_classes...")
    students_classes_file = current_dir / "students_classes.json"
    with open(students_classes_file, "r") as file:
        students_classes_data = json.load(file)

    students_classes_to_add = []
    for student_class_data in students_classes_data:
        result = await db.execute(
            select(StudentClass)
            .where(StudentClass.student_id == student_class_data["student_id"])
            .where(StudentClass.class_id == student_class_data["class_id"])
        )

        if not result.scalars().first():
            # Convert date string to Python date object
            if (
                "enrollment_date" in student_class_data
                and student_class_data["enrollment_date"]
            ):
                student_class_data["enrollment_date"] = datetime.strptime(
                    student_class_data["enrollment_date"], "%Y-%m-%d"
                ).date()

            students_classes_to_add.append(StudentClass(**student_class_data))
            print(
                f"  - Preparing to add students_classes data between student_id: {student_class_data['student_id']} and class_id:{student_class_data['class_id']}"
            )
        else:
            print(
                f"  - students_classes data between student_id: {student_class_data['student_id']} and class_id:{student_class_data['class_id']} already exists, skipping."
            )

    if students_classes_to_add:
        db.add_all(students_classes_to_add)
        print(
            f"  - Adding {len(students_classes_to_add)} new students_classes to the session."
        )
    else:
        print("  - No new students_classes to add.")
