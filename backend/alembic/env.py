# alembic/env.py
import asyncio
from logging.config import fileConfig
import sys
import os
from alembic import context
from app.core.config import settings
from app.db.base import Base

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


# Load Alembic configuration
config = context.config

# Setup Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = Base.metadata

# Ensure database URL is taken from environment settings
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")
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
