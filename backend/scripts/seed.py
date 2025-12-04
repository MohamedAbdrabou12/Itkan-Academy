import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from scripts.branches import add_branches
from scripts.permissions import add_permissions
from scripts.role_permissions import add_role_permissions
from scripts.roles import add_roles
from scripts.users import add_users
from scripts.students import add_students
from scripts.teachers import add_teachers
from scripts.user_branch import add_user_branch
from scripts.classes import add_classes
from scripts.student_classes import add_students_classes
from scripts.teacher_classes import add_teacher_classes
from scripts.parents import add_parents
from scripts.parent_students import add_parent_students

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
        await add_permissions(db)
        await add_role_permissions(db)
        await add_users(db)
        await add_user_branch(db)
        await add_students(db)
        await add_teachers(db)
        await add_classes(db)
        await add_students_classes(db)
        await add_teacher_classes(db)
        await add_parents(db)
        await add_parent_students(db)
        await db.commit()
        print("\nAll data committed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    print("--- Starting database seeding process ---")
    asyncio.run(seed_data())
    print("--- Database seeding finished ---")
