import json
from pathlib import Path

from app.modules.teachers.models import TeacherClass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_teacher_classes(db: AsyncSession):
    print("Seeding teacher_classes...")
    teacher_classes_file = current_dir / "teacher_classes.json"
    with open(teacher_classes_file, "r") as file:
        teacher_classes_data = json.load(file)

    teacher_classes_to_add = []
    for teacher_class_data in teacher_classes_data:
        result = await db.execute(
            select(TeacherClass)
            .where(TeacherClass.teacher_id == teacher_class_data["teacher_id"])
            .where(TeacherClass.class_id == teacher_class_data["class_id"])
        )

        if not result.scalars().first():
            # Convert date string to Python date object
            teacher_classes_to_add.append(TeacherClass(**teacher_class_data))
            print(
                f"  - Preparing to add teacher_classes data between teacher_id: {teacher_class_data['teacher_id']} and class_id:{teacher_class_data['class_id']}"
            )
        else:
            print(
                f"  - teacher_classes data between teacher_id: {teacher_class_data['teacher_id']} and class_id:{teacher_class_data['class_id']} already exists, skipping."
            )

    if teacher_classes_to_add:
        db.add_all(teacher_classes_to_add)
        print(
            f"  - Adding {len(teacher_classes_to_add)} new teacher_classes to the session."
        )
    else:
        print("  - No new teacher_classes to add.")
