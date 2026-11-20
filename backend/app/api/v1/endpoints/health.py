"""Health and readiness endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_session)) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "unreachable"}


@router.get("/ready")
async def readiness_check() -> dict:
    checks = {
        "api": "ok",
        "database": "unreachable",
        "redis": "unreachable",
    }
    return {"status": "not_ready", "checks": checks}
