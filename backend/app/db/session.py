"""SQLAlchemy database session and utilities."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_database_url, get_settings

settings = get_settings()
engine = create_async_engine(
    get_database_url(settings),
    pool_size=settings.sqlalchemy_pool_size,
    max_overflow=settings.sqlalchemy_max_overflow,
    echo=settings.debug,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
