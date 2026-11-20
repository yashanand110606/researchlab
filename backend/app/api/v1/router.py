"""API v1 router — mounts all endpoint routers."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import health, experiments, runs, datasets

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(experiments.router)
router.include_router(runs.router)
router.include_router(datasets.router)
