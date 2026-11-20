"""Experiment run management endpoints."""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.health import router as health_router
from app.db.session import get_session
from app.services.experiment_service import ExperimentService
from app.schemas.run import RunOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/experiments/{experiment_id}/runs", response_model=RunOut, status_code=201)
async def create_run(
    experiment_id: uuid.UUID,
    random_seed: int | None = Query(None),
    db: AsyncSession = Depends(get_session),
) -> RunOut:
    svc = ExperimentService(db)
    run = await svc.create_run(experiment_id, random_seed=random_seed)
    # Submit to Celery if broker is available; otherwise store as PENDING
    try:
        from app.workers.tasks import run_experiment_task
        result = run_experiment_task.apply_async(args=[str(run.id)], task_id=str(run.id))
        logger.info("Submitted run %s to Celery, task_id=%s", run.id, result.id)
    except Exception as exc:
        logger.warning("Celery unavailable, run %s stays PENDING: %s", run.id, exc)
    return RunOut.model_validate(run)


@router.get("", response_model=dict)
async def list_runs(
    experiment_id: str | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_session),
) -> dict:
    svc = ExperimentService(db)
    eid = uuid.UUID(experiment_id) if experiment_id else None
    runs = await svc.list_runs(experiment_id=eid, status=status, skip=skip, limit=limit)
    return {
        "items": [RunOut.model_validate(r).model_dump() for r in runs],
        "count": len(runs),
    }


@router.get("/{run_id}", response_model=RunOut)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_session)) -> RunOut:
    svc = ExperimentService(db)
    run = await svc.get_run(run_id)
    return RunOut.model_validate(run)


@router.post("/{run_id}/cancel", response_model=RunOut)
async def cancel_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_session)) -> RunOut:
    svc = ExperimentService(db)
    run = await svc.cancel_run(run_id)
    return RunOut.model_validate(run)


@router.post("/{run_id}/retry", response_model=RunOut, status_code=201)
async def retry_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_session)) -> RunOut:
    svc = ExperimentService(db)
    new_run = await svc.retry_run(run_id)
    try:
        from app.workers.tasks import run_experiment_task
        run_experiment_task.apply_async(args=[str(new_run.id)], task_id=str(new_run.id))
    except Exception as exc:
        logger.warning("Celery unavailable for retry %s: %s", new_run.id, exc)
    return RunOut.model_validate(new_run)


@router.get("/{run_id}/logs", response_model=dict)
async def get_run_logs(run_id: uuid.UUID, db: AsyncSession = Depends(get_session)) -> dict:
    svc = ExperimentService(db)
    logs = await svc.get_logs(run_id)
    entries = []
    for lg in logs:
        entries.append({
            "id": str(lg.id),
            "timestamp": lg.timestamp.isoformat(),
            "level": lg.level,
            "message": lg.message,
            "metadata": lg.metadata,
        })
    return {"items": entries, "count": len(entries)}


@router.get("/{run_id}/metrics", response_model=dict)
async def get_run_metrics(run_id: uuid.UUID, db: AsyncSession = Depends(get_session)) -> dict:
    svc = ExperimentService(db)
    metrics = await svc.get_metrics(run_id)
    items = []
    for m in metrics:
        items.append({
            "id": str(m.id),
            "name": m.name,
            "value": m.value,
            "unit": m.unit,
            "recorded_at": m.recorded_at.isoformat() if m.recorded_at else None,
            "step": m.step,
            "metadata": m.metadata,
        })
    return {"items": items, "count": len(items)}


@router.get("/{run_id}/results")
async def get_run_results(run_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Return stored JSON results if available, or compile from metrics."""
    svc = ExperimentService(db)
    run = await svc.get_run(run_id)
    metrics = await svc.get_metrics(run_id)
    metric_map = {m.name: m for m in metrics}
    return {
        "run_id": str(run.id),
        "status": run.status,
        "duration_seconds": run.duration_seconds,
        "metrics": {k: v.value for k, v in metric_map.items()},
    }
