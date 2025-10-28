# alembic/env.py
from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context

from app.core.config import settings
from app.db.base import Base

# Import models so Alembic can detect them
from app.modules.users import models as user_models  # noqa: F401
from app.modules.branches import models as branch_models  # noqa: F401
from app.modules.exams import models as exam_models  # noqa: F401
from app.modules.financial import models as financial_models  # noqa: F401
from app.modules.reports import models as report_models  # noqa: F401


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
