# alembic/env.py
from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context

from app.core.config import settings
from app.db.base import Base

# Import models so Alembic can detect them
from app.modules.roles import models as role_models  # noqa: F401
from app.modules.permissions.models import permission as permission_models  # noqa: F401
from app.modules.permissions.models import permission_role as permission_role_models  # noqa: F401
from app.modules.classes import models as class_models  # noqa: F401
from app.modules.students import models as student_models  # noqa: F401
from app.modules.audits.models import audit_log as audit_models  # noqa: F401
from app.modules.attendance import models as attendance_models  # noqa: F401
from app.modules.notifications import models as notification_models  # noqa: F401
from app.modules.question_bank.models import QuestionBank as question_bank_models  # noqa: F401
from app.modules.evaluations.models import daily_evaluation as daily_evaluation_models  # noqa: F401
from app.modules.users import models as user_models  # noqa: F401
from app.modules.branches import models as branch_models  # noqa: F401
from app.modules.exams.models import exam as exam_models  # noqa: F401
from app.modules.exams.models import exam_answer as exam_answer_models  # noqa: F401
from app.modules.financial.models import payment as payment_models  # noqa: F401
from app.modules.reports.models import reports_job as reports_job_models  # noqa: F401
from app.modules.financial.models import invoice as invoice_models  # noqa: F401
from app.modules.exams.models import exam_question as exam_question_models  # noqa: F401
from app.modules.exams.models import exam_attempt as exam_attempt_models  # noqa: F401
from app.modules.staff.models import Staff as staff_models  # noqa: F401

# Load Alembic configuration
config = context.config

# Setup Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = Base.metadata

# Ensure database URL is taken from environment settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


# Run migrations in offline mode
def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Run migrations in online (async) mode
def run_migrations_online():
    connectable: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
        future=True,
    )

    async def do_run_migrations():
        async with connectable.connect() as async_conn:
            await async_conn.run_sync(run_migrations_sync)

    def run_migrations_sync(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_run_migrations())


# Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
