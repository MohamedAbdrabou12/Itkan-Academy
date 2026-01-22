import json
from datetime import datetime
from pathlib import Path

from app.modules.student_progress.models import StudentProgress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_student_progress(db: AsyncSession) -> None:
    print("Seeding student progress...")
    student_progress_file = current_dir / "student_progress.json"
    with Path.open(student_progress_file) as file:
        student_progress_data = json.load(file)

    student_progress_to_add = []
    for data in student_progress_data:
        result = await db.execute(select(StudentProgress).where(StudentProgress.id == data["id"]))

        if not result.scalars().first():
            if data.get("date"):
                data["date"] = datetime.fromisoformat(data["date"])

            student_progress_to_add.append(StudentProgress(**data))
            print(f"  - Preparing to add StudentProgress data {data['id']}")
        else:
            print(f"  - StudentProgress data {data['id']} already exists, skipping.")

    if student_progress_to_add:
        db.add_all(student_progress_to_add)
        print(f"  - Adding {len(student_progress_to_add)} new student progress to the session.")
    else:
        print("  - No new student progress to add.")
