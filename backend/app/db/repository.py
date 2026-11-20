"""Database repositories for experiments, runs, metrics, datasets."""
from __future__ import annotations

import uuid
from typing import Sequence
from datetime import datetime

from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Experiment,
    ExperimentRun,
    Metric,
    Dataset,
    ExperimentTag,
    ExperimentLog,
)
from app.schemas.experiment import ExperimentListParams, PaginationMeta


class ExperimentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self, params: ExperimentListParams) -> tuple[list[Experiment], PaginationMeta]:
        q = select(Experiment)
        if params.category:
            q = q.where(Experiment.category == params.category)
        if params.search:
            search = f"%{params.search}%"
            q = q.where(Experiment.name.ilike(search) | Experiment.description.ilike(search))

        total_q = select(func.count()).select_from(q.subquery())
        total = (await self._session.execute(total_q)).scalar_one()

        sort_col = getattr(Experiment, params.sort_by, Experiment.created_at)
        if params.sort_order == "desc":
            q = q.order_by(sort_col.desc())
        else:
            q = q.order_by(sort_col.asc())
        q = q.offset(params.skip).limit(params.limit)

        result = await self._session.execute(q)
        return list(result.scalars().all()), PaginationMeta(total=total, skip=params.skip, limit=params.limit)

    async def get(self, experiment_id: uuid.UUID) -> Experiment | None:
        return await self._session.get(Experiment, experiment_id)

    async def create(self, name: str, description: str | None, category: str, configuration: dict) -> Experiment:
        exp = Experiment(name=name, description=description, category=category, configuration=configuration)
        self._session.add(exp)
        await self._session.flush()
        await self._session.refresh(exp)
        return exp

    async def update(self, experiment_id: uuid.UUID, **kwargs) -> Experiment | None:
        stmt = update(Experiment).where(Experiment.id == experiment_id).values(**kwargs).returning(Experiment)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()

    async def delete(self, experiment_id: uuid.UUID) -> bool:
        stmt = delete(Experiment).where(Experiment.id == experiment_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0


class RunRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(
        self,
        experiment_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ExperimentRun]:
        q = select(ExperimentRun)
        if experiment_id:
            q = q.where(ExperimentRun.experiment_id == experiment_id)
        if status:
            q = q.where(ExperimentRun.status == status)
        q = q.order_by(ExperimentRun.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(q)
        return list(result.scalars().all())

    async def get(self, run_id: uuid.UUID) -> ExperimentRun | None:
        return await self._session.get(ExperimentRun, run_id)

    async def create(self, run: ExperimentRun) -> ExperimentRun:
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def update_status(self, run_id: uuid.UUID, status: str) -> ExperimentRun | None:
        stmt = (
            update(ExperimentRun)
            .where(ExperimentRun.id == run_id)
            .values(status=status)
            .returning(ExperimentRun)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()

    async def mark_started(self, run_id: uuid.UUID, worker_id: str) -> ExperimentRun | None:
        now = datetime.now(tz=__import__('datetime').timezone.utc)
        stmt = (
            update(ExperimentRun)
            .where(ExperimentRun.id == run_id)
            .values(status="RUNNING", started_at=now, worker_id=worker_id)
            .returning(ExperimentRun)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()

    async def mark_completed(self, run_id: uuid.UUID, duration_seconds: float) -> ExperimentRun | None:
        now = datetime.now(tz=datetime.now(tz=__import__('datetime').timezone.utc).tzinfo)
        stmt = (
            update(ExperimentRun)
            .where(ExperimentRun.id == run_id)
            .values(status="COMPLETED", completed_at=now, duration_seconds=duration_seconds)
            .returning(ExperimentRun)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()

    async def mark_failed(self, run_id: uuid.UUID, error_message: str) -> ExperimentRun | None:
        now = datetime.now(tz=__import__('datetime').timezone.utc)
        stmt = (
            update(ExperimentRun)
            .where(ExperimentRun.id == run_id)
            .values(status="FAILED", completed_at=now, error_message=error_message)
            .returning(ExperimentRun)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()


class MetricRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_by_run(self, run_id: uuid.UUID) -> list[Metric]:
        stmt = select(Metric).where(Metric.run_id == run_id).order_by(Metric.recorded_at)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, metric: Metric) -> Metric:
        self._session.add(metric)
        await self._session.flush()
        return metric

    async def add_many(self, metrics: list[Metric]) -> None:
        self._session.add_all(metrics)
        await self._session.commit()


class DatasetRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self, skip: int = 0, limit: int = 50) -> tuple[list[Dataset], int]:
        total = (await self._session.execute(select(func.count()).select_from(Dataset))).scalar_one()
        stmt = select(Dataset).order_by(Dataset.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def get(self, dataset_id: uuid.UUID) -> Dataset | None:
        return await self._session.get(Dataset, dataset_id)

    async def create(self, dataset: Dataset) -> Dataset:
        self._session.add(dataset)
        await self._session.flush()
        await self._session.refresh(dataset)
        return dataset

    async def delete(self, dataset_id: uuid.UUID) -> bool:
        stmt = delete(Dataset).where(Dataset.id == dataset_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0


class TagRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, experiment_id: uuid.UUID, tag: str) -> ExperimentTag:
        t = ExperimentTag(experiment_id=experiment_id, tag=tag)
        self._session.add(t)
        await self._session.flush()
        return t

    async def remove(self, experiment_id: uuid.UUID, tag: str) -> bool:
        stmt = delete(ExperimentTag).where(
            ExperimentTag.experiment_id == experiment_id,
            ExperimentTag.tag == tag,
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def list_for_experiment(self, experiment_id: uuid.UUID) -> list[ExperimentTag]:
        stmt = select(ExperimentTag).where(ExperimentTag.experiment_id == experiment_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
