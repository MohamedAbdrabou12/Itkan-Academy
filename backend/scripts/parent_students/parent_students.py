import json
from pathlib import Path
from app.modules.parents.models import ParentStudent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_parent_students(db: AsyncSession):
    print("Seeding parent-student relations...")
    relations_file = current_dir / "parent_students.json"
    with open(relations_file, "r") as file:
        relations_data = json.load(file)

    relations_to_add = []
    for rel in relations_data:
        result = await db.execute(
            select(ParentStudent).where(
                ParentStudent.parent_id == rel["parent_id"],
                ParentStudent.student_id == rel["student_id"],
            )
        )

        if not result.scalars().first():
            relations_to_add.append(ParentStudent(**rel))
            print(
                f"  - Preparing to link Parent {rel['parent_id']} -> Student {rel['student_id']}"
            )
        else:
            print(
                f"  - Relation Parent {rel['parent_id']} -> Student {rel['student_id']} exists, skipping."
            )

    if relations_to_add:
        db.add_all(relations_to_add)
        print(f"  - Added {len(relations_to_add)} parent-student relations.")
    else:
        print("  - No new parent-student relations to add.")
