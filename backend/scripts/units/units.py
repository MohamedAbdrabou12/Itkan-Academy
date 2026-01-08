import json
from pathlib import Path

from app.modules.curriculums.models.unit import Unit, UnitItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_units(db: AsyncSession) -> None:
    print("Seeding units...")
    units_file = current_dir / "units.json"
    with Path.open(units_file) as file:
        units_data: list[dict] = json.load(file)

    units_to_add = []
    unit_items_to_add = []
    for unit_data in units_data:
        result = await db.execute(select(Unit).where(Unit.id == unit_data["id"]))

        if not result.scalars().first():
            items_data: list[dict] = unit_data.pop("items")
            units_to_add.append(Unit(**unit_data))
            print(f"  - Preparing to add Unit data {unit_data['title']}")
            for item_data in items_data:
                result = await db.execute(select(UnitItem).where(UnitItem.id == item_data["id"]))

                if not result.scalars().first():
                    item_data["unit_id"] = unit_data["id"]
                    unit_items_to_add.append(UnitItem(**item_data))
                    print(f"    - Preparing to add UnitItem data {item_data['title']}")
                else:
                    print(
                        f"    - UnitItem data {unit_data['title']} already exists, skipping."
                    )
        else:
            print(f"  - Unit data {unit_data['title']} already exists, skipping.")

    if units_to_add:
        db.add_all(units_to_add)
        print(f"  - Adding {len(units_to_add)} new units to the session.")
    else:
        print("  - No new units to add.")

    if unit_items_to_add:
        db.add_all(unit_items_to_add)
        print(f"  - Adding {len(unit_items_to_add)} new unit items to the session.")
    else:
        print("  - No new unit items to add.")
