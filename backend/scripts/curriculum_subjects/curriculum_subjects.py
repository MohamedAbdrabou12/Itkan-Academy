import json
from operator import and_
from pathlib import Path

from app.modules.curriculums.models.curriculum import CurriculumSubject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_curriculum_subjects(db: AsyncSession) -> None:
    print("Seeding curriculum subjects...")
    curriculum_subjects_file = current_dir / "curriculum_subjects.json"
    with Path.open(curriculum_subjects_file) as file:
        curriculum_subjects_data = json.load(file)

    curriculum_subjects_to_add = []
    for curriculum_subject_data in curriculum_subjects_data:
        result = await db.execute(
            select(CurriculumSubject).where(
                and_(
                    CurriculumSubject.curriculum_id == curriculum_subject_data["curriculum_id"],
                    CurriculumSubject.subject_id == curriculum_subject_data["subject_id"],
                )
            )
        )

        if not result.scalars().first():
            curriculum_subjects_to_add.append(CurriculumSubject(**curriculum_subject_data))
            print(
                f"  - Preparing to add CurriculumSubject data between curriculum_id: {curriculum_subject_data['curriculum_id']} and subject_id: {curriculum_subject_data['subject_id']}"
            )
        else:
            print(
                f"  - CurriculumSubject data between curriculum_id: {curriculum_subject_data['curriculum_id']} and subject_id: {curriculum_subject_data['subject_id']} already exists, skipping."
            )

    if curriculum_subjects_to_add:
        db.add_all(curriculum_subjects_to_add)
        print(
            f"  - Adding {len(curriculum_subjects_to_add)} new curriculum subjects to the session."
        )
    else:
        print("  - No new curriculum subjects to add.")
