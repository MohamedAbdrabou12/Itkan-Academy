from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# استيراد إعدادات المشروع
from app.core.config import settings
from app.db.base import Base

# استيراد جميع الموديلات للموديولات عشان autogenerate
from app.modules.users import models as user_models
from app.modules.branches import models as branch_models
from app.modules.exams import models as exam_models
from app.modules.financial import models as financial_models

# إعداد Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.DATABASE_URL,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
