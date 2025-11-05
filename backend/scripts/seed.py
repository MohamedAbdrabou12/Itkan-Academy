import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.branches import add_branches
from scripts.roles import add_roles
from app.core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


async def seed_data():
    print("Seeding data...", settings.DATABASE_URL)
    if not settings.DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please configure it in your .env file."
        )

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    async with AsyncSessionLocal() as db:
        await add_branches(db)
        await add_roles(db)
        await db.commit()
        print("\nAll data committed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    print("--- Starting database seeding process ---")
    asyncio.run(seed_data())
    print("--- Database seeding finished ---")
