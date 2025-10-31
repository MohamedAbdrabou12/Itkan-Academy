# app/db/session.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create async SQLAlchemy engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENV == "development"),  # Show SQL logs only in development
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


# Provide a database session for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Helper for Alembic or manual DB access
def get_engine() -> AsyncEngine:
    return engine
