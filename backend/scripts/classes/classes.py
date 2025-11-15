import json
from pathlib import Path

from app.modules.classes.models import Class
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_classes(db: AsyncSession):
    print("Seeding classes...")
    classes_file = current_dir / "classes.json"
    with open(classes_file, "r") as file:
        classes_data = json.load(file)

    classes_to_add = []
    for class_data in classes_data:
        result = await db.execute(select(Class).where(Class.id == class_data["id"]))

        if not result.scalars().first():
            classes_to_add.append(Class(**class_data))
            print(f"  - Preparing to add Classes data {class_data['name']}")
        else:
            print(f"  - Classes data {class_data['name']} already exists, skipping.")

    if classes_to_add:
        db.add_all(classes_to_add)
        print(f"  - Adding {len(classes_to_add)} new classes to the session.")
    else:
        print("  - No new classes to add.")
