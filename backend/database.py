"""
Database configuration and session management.
Supports both PostgreSQL+PostGIS (production) and SQLite (local dev).
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.config import get_settings

settings = get_settings()

# SQLite doesn't support pool_size / max_overflow
engine_kwargs = {"echo": False}
if not settings.is_sqlite:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting an async database session.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_all_tables():
    """
    Create all database tables. Used for SQLite local dev
    (in production, use Alembic migrations with PostGIS).
    """
    from backend.models.base import Base
    # Import all models to register them with Base.metadata
    import backend.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
