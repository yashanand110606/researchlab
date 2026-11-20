"""Pytest fixtures for async testing with SQLite."""
from __future__ import annotations

import asyncio
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_in_memory_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
_InMemorySessionLocal = async_sessionmaker(_in_memory_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def app():
    """FastAPI app using in-memory SQLite instead of real PostgreSQL."""
    from app.main import app as real_app
    from app.db.session import get_session

    async with _in_memory_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _fake_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with _InMemorySessionLocal() as session:
            yield session

    real_app.dependency_overrides[get_session] = _fake_get_session
    return real_app


@pytest_asyncio.fixture
async def db_session(app: FastAPI) -> AsyncGenerator[AsyncSession, None]:
    """Fresh in-memory session per test."""
    async with _InMemorySessionLocal() as session:
        yield session
        await session.rollback()
