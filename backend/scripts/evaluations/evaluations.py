from datetime import datetime
import json
from pathlib import Path

from app.modules.evaluations.models import Evaluation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

current_dir = Path(__file__).resolve().parent


async def add_evaluations(db: AsyncSession):
    print("Seeding evaluations...")
    evaluations_file = current_dir / "evaluations.json"
    with open(evaluations_file, "r") as file:
        evaluations_data = json.load(file)

    evaluations_to_add = []
    for evaluation_data in evaluations_data:
        result = await db.execute(
            select(Evaluation).where(Evaluation.id == evaluation_data["id"])
        )

        if not result.scalars().first():
            if "date" in evaluation_data and evaluation_data["date"]:
                evaluation_data["date"] = datetime.fromisoformat(
                    evaluation_data["date"]
                )

            evaluations_to_add.append(Evaluation(**evaluation_data))
            print(f"  - Preparing to add Evaluations data {evaluation_data['id']}")
        else:
            print(
                f"  - Evaluations data {evaluation_data['id']} already exists, skipping."
            )

    if evaluations_to_add:
        db.add_all(evaluations_to_add)
        print(f"  - Adding {len(evaluations_to_add)} new evaluations to the session.")
    else:
        print("  - No new evaluations to add.")
