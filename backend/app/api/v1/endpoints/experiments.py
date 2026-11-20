"""Experiment CRUD and management endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import ExperimentRepository, TagRepository
from app.db.session import get_session
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentOut,
    ExperimentUpdate,
    ExperimentListParams,
    PaginationMeta,
    TagAdd,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=dict)
async def list_experiments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_session),
) -> dict:
    params = ExperimentListParams(
        skip=skip, limit=limit, category=category, search=search,
        sort_by=sort_by, sort_order=sort_order,
    )
    repo = ExperimentRepository(db)
    items, meta = await repo.list(params)
    return {
        "items": [ExperimentOut.model_validate(i).model_dump() for i in items],
        "pagination": meta.model_dump(),
    }


@router.post("", response_model=ExperimentOut, status_code=201)
async def create_experiment(
    data: ExperimentCreate,
    db: AsyncSession = Depends(get_session),
) -> ExperimentOut:
    repo = ExperimentRepository(db)
    exp = await repo.create(data.name, data.description, data.category, data.configuration)
    return ExperimentOut.model_validate(exp)


@router.get("/types")
async def list_experiment_types(
    db: AsyncSession = Depends(get_session),
) -> dict:
    from app.experiments.registry import list_experiment_types, get_experiment_class
    types = list_experiment_types()
    results = []
    for t in types:
        cls = get_experiment_class(t)
        inst = cls()
        results.append(inst.describe())
    return {"types": types, "details": results}


@router.get("/{experiment_id}", response_model=ExperimentOut)
async def get_experiment(
    experiment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> ExperimentOut:
    repo = ExperimentRepository(db)
    exp = await repo.get(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")
    return ExperimentOut.model_validate(exp)


@router.patch("/{experiment_id}", response_model=ExperimentOut)
async def update_experiment(
    experiment_id: uuid.UUID,
    data: ExperimentUpdate,
    db: AsyncSession = Depends(get_session),
) -> ExperimentOut:
    repo = ExperimentRepository(db)
    updates = data.model_dump(exclude_none=True)
    if "configuration" in updates and updates["configuration"] is not None:
        existing = await repo.get(experiment_id)
        if existing:
            updates["configuration_version"] = 1 + existing.configuration_version
    if not updates:
        exp = await repo.get(experiment_id)
        if not exp:
            raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")
        return ExperimentOut.model_validate(exp)
    exp = await repo.update(experiment_id, **updates)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")
    return ExperimentOut.model_validate(exp)


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> None:
    repo = ExperimentRepository(db)
    ok = await repo.delete(experiment_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found")


@router.post("/{experiment_id}/duplicate", response_model=ExperimentOut, status_code=201)
async def duplicate_experiment(
    experiment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> ExperimentOut:
    from app.services.experiment_service import ExperimentService
    svc = ExperimentService(db)
    exp = await svc.duplicate_experiment(experiment_id)
    return ExperimentOut.model_validate(exp)


@router.post("/{experiment_id}/tags", response_model=dict)
async def add_tag(
    experiment_id: uuid.UUID,
    data: TagAdd,
    db: AsyncSession = Depends(get_session),
) -> dict:
    repo = TagRepository(db)
    tag = await repo.add(experiment_id, data.tag)
    return {"id": str(tag.id), "tag": tag.tag}


@router.delete("/{experiment_id}/tags/{tag}")
async def remove_tag(
    experiment_id: uuid.UUID,
    tag: str,
    db: AsyncSession = Depends(get_session),
) -> dict:
    repo = TagRepository(db)
    ok = await repo.remove(experiment_id, tag)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Tag '{tag}' not found on experiment")
    return {"deleted": True, "tag": tag}
