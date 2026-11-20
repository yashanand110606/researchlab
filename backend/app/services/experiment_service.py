"""Business logic services for experiments and runs."""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError, ValidationErrorDetail
from app.db.models import Experiment, ExperimentRun
from app.db.repository import ExperimentRepository, RunRepository, MetricRepository, TagRepository, DatasetRepository
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate, ExperimentListParams, PaginationMeta
from app.schemas.run import VALID_TRANSITIONS

logger = logging.getLogger(__name__)


class ExperimentService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._exp_repo = ExperimentRepository(session)
        self._run_repo = RunRepository(session)
        self._metric_repo = MetricRepository(session)
        self._tag_repo = TagRepository(session)
        self._dataset_repo = DatasetRepository(session)

    # ── Experiments ────────────────────────────────────────────────

    async def list_experiments(self, params: ExperimentListParams) -> tuple[list[Experiment], PaginationMeta]:
        return await self._exp_repo.list(params)

    async def get_experiment(self, experiment_id: uuid.UUID) -> Experiment:
        exp = await self._exp_repo.get(experiment_id)
        if not exp:
            raise NotFoundError("Experiment", experiment_id)
        return exp

    async def create_experiment(self, data: ExperimentCreate) -> Experiment:
        return await self._exp_repo.create(
            name=data.name,
            description=data.description,
            category=data.category,
            configuration=data.configuration,
        )

    async def update_experiment(self, experiment_id: uuid.UUID, data: ExperimentUpdate) -> Experiment | None:
        updates = data.model_dump(exclude_none=True)
        if "configuration" in updates and updates["configuration"] is not None:
            updates["configuration_version"] = 1 + (await self._exp_repo.get(experiment_id)).configuration_version
        if not updates:
            return await self._exp_repo.get(experiment_id)
        return await self._exp_repo.update(experiment_id, **updates)

    async def delete_experiment(self, experiment_id: uuid.UUID) -> bool:
        exists = await self._exp_repo.get(experiment_id)
        if not exists:
            raise NotFoundError("Experiment", experiment_id)
        return await self._exp_repo.delete(experiment_id)

    async def duplicate_experiment(self, experiment_id: uuid.UUID) -> Experiment:
        src = await self._exp_repo.get(experiment_id)
        if not src:
            raise NotFoundError("Experiment", experiment_id)
        new_exp = await self._exp_repo.create(
            name=f"{src.name} (copy)",
            description=src.description,
            category=src.category,
            configuration=dict(src.configuration),
        )
        for tag in src.tags:
            await self._tag_repo.add(new_exp.id, tag.tag)
        return new_exp

    async def add_tag(self, experiment_id: uuid.UUID, tag_value: str) -> dict:
        exp = await self._exp_repo.get(experiment_id)
        if not exp:
            raise NotFoundError("Experiment", experiment_id)
        t = await self._tag_repo.add(experiment_id, tag_value)
        return {"id": str(t.id), "tag": t.tag}

    async def remove_tag(self, experiment_id: uuid.UUID, tag_value: str) -> bool:
        return await self._tag_repo.remove(experiment_id, tag_value)

    # ── Runs ───────────────────────────────────────────────────────

    async def create_run(self, experiment_id: uuid.UUID, random_seed: int | None = None) -> ExperimentRun:
        exp = await self._exp_repo.get(experiment_id)
        if not exp:
            raise NotFoundError("Experiment", experiment_id)

        snapshot = {
            "type": exp.configuration.get("experiment", {}).get("type", ""),
            "parameters": exp.configuration.get("experiment", {}).get("parameters", {}),
            "execution": exp.configuration.get("experiment", {}).get("execution", {}),
            "_source_experiment_id": str(experiment_id),
            "_config_hash": hashlib.sha256(json.dumps(exp.configuration, sort_keys=True).encode()).hexdigest()[:16],
        }

        run = ExperimentRun(
            experiment_id=experiment_id,
            status="PENDING",
            configuration_snapshot=snapshot,
            random_seed=random_seed,
        )
        return await self._run_repo.create(run)

    async def list_runs(
        self,
        experiment_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ExperimentRun]:
        return await self._run_repo.list(experiment_id=experiment_id, status=status, skip=skip, limit=limit)

    async def get_run(self, run_id: uuid.UUID) -> ExperimentRun:
        run = await self._run_repo.get(run_id)
        if not run:
            raise NotFoundError("Run", run_id)
        return run

    async def cancel_run(self, run_id: uuid.UUID) -> ExperimentRun:
        run = await self._run_repo.get(run_id)
        if not run:
            raise NotFoundError("Run", run_id)
        if run.status not in VALID_TRANSITIONS.get("QUEUED", set()) | {"PENDING"}:
            if run.status in ("COMPLETED", "FAILED"):
                raise ConflictError(f"Cannot cancel run in state '{run.status}'")
        new_status = "CANCELLED" if run.status in ("PENDING", "QUEUED") else run.status
        if new_status != run.status:
            run = await self._run_repo.update_status(run_id, new_status)
        return run or await self._run_repo.get(run_id)

    async def retry_run(self, run_id: uuid.UUID) -> ExperimentRun:
        run = await self._run_repo.get(run_id)
        if not run:
            raise NotFoundError("Run", run_id)
        if run.status not in ("FAILED", "CANCELLED"):
            raise ConflictError(f"Can only retry runs in FAILED or CANCELLED state, got {run.status!r}")
        new_run = ExperimentRun(
            experiment_id=run.experiment_id,
            status="PENDING",
            configuration_snapshot=dict(run.configuration_snapshot),
            random_seed=run.random_seed,
        )
        return await self._run_repo.create(new_run)

    async def get_metrics(self, run_id: uuid.UUID) -> list[Any]:
        from app.db.models import Metric
        return await self._metric_repo.list_by_run(run_id)

    async def get_logs(self, run_id: uuid.UUID) -> list[Any]:
        from app.db.models import ExperimentLog
        stmt = (
            __import__('sqlalchemy').select(ExperimentLog)
            .where(ExperimentLog.run_id == run_id)
            .order_by(ExperimentLog.timestamp)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
