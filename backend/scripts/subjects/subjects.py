import json
from pathlib import Path

from app.modules.curriculums.models.subject import Subject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_subjects(db: AsyncSession) -> None:
    print("Seeding subjects...")
    subjects_file = current_dir / "subjects.json"
    with Path.open(subjects_file) as file:
        subjects_data = json.load(file)

    subjects_to_add = []
    for subject_data in subjects_data:
        result = await db.execute(select(Subject).where(Subject.id == subject_data["id"]))

        if not result.scalars().first():
            subjects_to_add.append(Subject(**subject_data))
            print(f"  - Preparing to add Subject data {subject_data['name']}")
        else:
            print(f"  - Subject data {subject_data['name']} already exists, skipping.")

    if subjects_to_add:
        db.add_all(subjects_to_add)
        print(f"  - Adding {len(subjects_to_add)} new subjects to the session.")
    else:
        print("  - No new subjects to add.")
