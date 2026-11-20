"""Experiment execution engine — orchestrates experiment lifecycle."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ExperimentRun, ExperimentLog, Metric
from app.experiments.base import BaseExperiment
from app.experiments.registry import get_experiment_class

logger = logging.getLogger(__name__)


async def execute_experiment(
    session: AsyncSession,
    run_id: uuid.UUID,
) -> None:
    """Execute a single experiment run synchronously within an async context.

    This is called by the Celery task (via run_in_executor) so that we can
    interact with the async SQLAlchemy session without mixing sync/async IO.
    """
    run = await session.get(ExperimentRun, run_id)
    if run is None:
        logger.error("Run %s not found", run_id)
        return

    now = datetime.now(tz=timezone.utc)
    run.started_at = now
    run.status = "RUNNING"
    run.worker_id = f"worker-{uuid.uuid4().hex[:8]}"
    await session.commit()

    log_id = uuid.uuid4()
    run_log = ExperimentLog(
        run_id=run_id,
        timestamp=now,
        level="INFO",
        message=f"Execution started (run={run_id})",
    )
    session.add(run_log)
    await session.flush()

    try:
        exp_cls = get_experiment_class(run.configuration_snapshot.get("type", ""))
        ctx = type("Ctx", (), {
            "config": run.configuration_snapshot,
            "random_seed": run.random_seed or 42,
            "experiment_id": str(run.experiment_id),
            "run_id": str(run_id),
            "logs": [],
            "metrics": [],
            "start_time": __import__("time").monotonic(),
            "errors": [],
            "log": lambda level, msg, metadata=None: _add_log(session, run_id, level, msg, metadata),
            "record_metric": lambda name, value, unit=None, step=None, extra=None: _add_metric(session, run_id, name, value, unit, step, extra),
            "duration": property(lambda self: __import__("time").monotonic() - __import__("time").monotonic()),
        })()
        # Proper ExperimentContext via import
        from app.experiments.base import ExperimentContext
        ctx2 = ExperimentContext(
            config=run.configuration_snapshot,
            random_seed=run.random_seed or 42,
            experiment_id=str(run.experiment_id),
            run_id=str(run_id),
        )

        validator_errors = exp_cls.validate_config(run.configuration_snapshot)
        if validator_errors:
            err_msg = "; ".join(validator_errors)
            raise ValueError(f"Configuration validation failed: {err_msg}")

        results = await asyncio.to_thread(exp_cls.execute, ctx2)

        completed_at = datetime.now(tz=timezone.utc)
        duration = (completed_at - run.started_at).total_seconds()

        run.status = "COMPLETED"
        run.completed_at = completed_at
        run.duration_seconds = duration
        await session.commit()

        for entry in ctx2.logs:
            sid = uuid.uuid4()
            lg = ExperimentLog(run_id=run_id, timestamp=datetime.fromtimestamp(entry["timestamp"], tz=timezone.utc),
                                level=entry["level"], message=entry["message"], metadata=entry.get("metadata"))
            session.add(lg)
        for m in ctx2.metrics:
            mid = uuid.uuid4()
            mt = Metric(run_id=run_id, name=m["name"], value=m["value"], unit=m.get("unit"),
                        recorded_at=datetime.now(tz=timezone.utc), step=m.get("step"),
                        metadata={"result_key": m.get("name")})
            session.add(mt)
        await session.commit()

        logger.info("Run %s completed in %.2fs with %d metrics", run_id, duration, len(ctx2.metrics))

    except Exception as exc:
        logger.exception("Run %s failed: %s", run_id, exc)
        error_msg = str(exc)[:4000]
        await session.execute(
            ExperimentRun.__table__.update()
            .where(ExperimentRun.id == run_id)
            .values(status="FAILED", completed_at=datetime.now(tz=timezone.utc), error_message=error_msg)
        )
        await session.commit()


def _add_log(session: AsyncSession, run_id: uuid.UUID, level: str, message: str, metadata: dict | None = None) -> None:
    """Helper for ExperimentContext.log (sync context)."""
    import time as _time
    lg = ExperimentLog(
        run_id=run_id,
        timestamp=datetime.fromtimestamp(_time.time(), tz=__import__('datetime').timezone.utc),
        level=level,
        message=message,
        metadata=metadata,
    )
    session.add(lg)


def _add_metric(session: AsyncSession, run_id: uuid.UUID, name: str, value: float,
                unit: str | None, step: int | None, extra: dict | None) -> None:
    mt = Metric(
        run_id=run_id, name=name, value=value, unit=unit,
        recorded_at=datetime.now(tz=__import__('datetime').timezone.utc),
        step=step, metadata=extra,
    )
    session.add(mt)
