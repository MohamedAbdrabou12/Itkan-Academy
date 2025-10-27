from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context
import asyncio

from app.core.config import settings
from app.db.base import Base
from app.modules.users import models as user_models
from app.modules.branches import models as branch_models
from app.modules.exams import models as exam_models
from app.modules.financial import models as financial_models

# Alembic config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Use AsyncEngine but run Alembic sync operations inside run_sync."""
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    async def do_run_migrations():
        async with connectable.connect() as async_conn:
            # استخدم run_sync لتشغيل السياق الـ Alembic على Connection عادي
            await async_conn.run_sync(sync_run_migrations)

    def sync_run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


# from logging.config import fileConfig
# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy import pool
# from alembic import context
# import asyncio

# from app.core.config import settings
# from app.db.base import Base
# from app.modules.users import models as user_models
# from app.modules.branches import models as branch_models
# from app.modules.exams import models as exam_models
# from app.modules.financial import models as financial_models

# # Alembic config object
# config = context.config

# # Set up Python logging from config file
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# # Metadata for autogenerate support
# target_metadata = Base.metadata
# config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode (generates SQL scripts without DB connection)."""
#     context.configure(
#         url=settings.DATABASE_URL,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )
#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode (executes against the DB asynchronously)."""
#     connectable = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

#     async def do_run_migrations():
#         async with connectable.connect() as connection:
#             # Configure Alembic context with live connection
#             await connection.run_sync(
#                 lambda conn: context.configure(
#                     connection=conn, target_metadata=target_metadata
#                 )
#             )
#             async with connection.begin():
#                 await connection.run_sync(context.run_migrations)

#     asyncio.run(do_run_migrations())


# # Choose mode based on Alembic context
# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()
