import json
from pathlib import Path

from app.modules.curriculums.models.subject_unit import SubjectUnit, SubjectUnitItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_subject_units(db: AsyncSession) -> None:
    print("Seeding subject units...")
    subject_units_file = current_dir / "subject_units.json"
    with Path.open(subject_units_file) as file:
        subject_units_data: list[dict] = json.load(file)

    subject_units_to_add = []
    subject_unit_items_to_add = []
    for subject_unit_data in subject_units_data:
        result = await db.execute(
            select(SubjectUnit).where(SubjectUnit.id == subject_unit_data["id"])
        )

        if not result.scalars().first():
            items_data: list[dict] = subject_unit_data.pop("items")
            subject_units_to_add.append(SubjectUnit(**subject_unit_data))
            print(f"  - Preparing to add SubjectUnit data {subject_unit_data['title']}")
            for item_data in items_data:
                result = await db.execute(
                    select(SubjectUnitItem).where(SubjectUnitItem.id == item_data["id"])
                )

                if not result.scalars().first():
                    item_data["unit_id"] = subject_unit_data["id"]
                    subject_unit_items_to_add.append(SubjectUnitItem(**item_data))
                    print(f"    - Preparing to add SubjectUnitItem data {item_data['title']}")
                else:
                    print(
                        f"    - SubjectUnitItem data {subject_unit_data['title']} already exists, skipping."
                    )
        else:
            print(f"  - SubjectUnit data {subject_unit_data['title']} already exists, skipping.")

    if subject_units_to_add:
        db.add_all(subject_units_to_add)
        print(f"  - Adding {len(subject_units_to_add)} new subject units to the session.")
    else:
        print("  - No new subject units to add.")

    if subject_unit_items_to_add:
        db.add_all(subject_unit_items_to_add)
        print(f"  - Adding {len(subject_unit_items_to_add)} new subject unit items to the session.")
    else:
        print("  - No new subject unit items to add.")
