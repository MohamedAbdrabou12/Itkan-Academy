# app/db/session.py
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create Async SQLAlchemy Engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Show SQL logs in console (optional)
    future=True,  # Enable 2.0 style usage
)

# Create Async Session Factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


# Dependency for FastAPI Routes
@asynccontextmanager
async def get_db_session():
    async with async_session() as session:
        yield session


# Helper for Alembic Async Migrations
def get_engine() -> AsyncEngine:
    return engine


# # Helper to get a new session
# def get_session() -> AsyncSession:    #we can use this in services
#     return async_session()
