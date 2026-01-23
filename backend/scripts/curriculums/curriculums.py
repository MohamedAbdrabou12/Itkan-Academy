import json
from pathlib import Path

from app.modules.curriculums.models.curriculum import Curriculum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_curriculums(db: AsyncSession) -> None:
    print("Seeding curriculums...")
    curriculums_file = current_dir / "curriculums.json"
    with Path.open(curriculums_file) as file:
        curriculums_data = json.load(file)

    curriculums_to_add = []
    for curriculum_data in curriculums_data:
        result = await db.execute(select(Curriculum).where(Curriculum.id == curriculum_data["id"]))

        if not result.scalars().first():
            curriculums_to_add.append(Curriculum(**curriculum_data))
            print(f"  - Preparing to add Curriculum data {curriculum_data['name']}")
        else:
            print(f"  - Curriculum data {curriculum_data['name']} already exists, skipping.")

    if curriculums_to_add:
        db.add_all(curriculums_to_add)
        print(f"  - Adding {len(curriculums_to_add)} new curriculums to the session.")
    else:
        print("  - No new curriculums to add.")
