import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from scripts.branches import add_branches
from scripts.classes import add_classes
from scripts.curriculum_subjects.curriculum_subjects import add_curriculum_subjects
from scripts.curriculums import add_curriculums
from scripts.evaluations import add_evaluations
from scripts.parent_students import add_parent_students
from scripts.parents import add_parents
from scripts.permissions import add_permissions
from scripts.role_permissions import add_role_permissions
from scripts.roles import add_roles
from scripts.student_classes import add_students_classes
from scripts.student_progress import add_student_progress
from scripts.students import add_students
from scripts.subjects.subjects import add_subjects
from scripts.teacher_classes import add_teacher_classes
from scripts.teachers import add_teachers
from scripts.units.units import add_units
from scripts.user_branch import add_user_branch
from scripts.users import add_users
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


async def seed_data():
    if not settings.DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is not set. Please configure it in your .env file."
        )

    print("Seeding data...", settings.DATABASE_URL)
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncSessionLocal() as db:
        await add_branches(db)
        await add_roles(db)
        await add_permissions(db)
        await add_role_permissions(db)
        await add_users(db)
        await add_user_branch(db)
        await add_students(db)
        await add_teachers(db)
        await add_curriculums(db)
        await add_subjects(db)
        await add_curriculum_subjects(db)
        await add_units(db)
        await add_classes(db)
        await add_students_classes(db)
        await add_teacher_classes(db)
        await add_parents(db)
        await add_parent_students(db)
        await add_evaluations(db)
        await add_student_progress(db)
        await db.commit()
        print("\nAll data committed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    print("--- Starting database seeding process ---")
    asyncio.run(seed_data())
    print("--- Database seeding finished ---")
