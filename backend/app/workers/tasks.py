"""Celery tasks for asynchronous experiment execution."""
from __future__ import annotations

import asyncio
import logging
import time

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.experiments.base import ExperimentContext
from app.experiments.registry import get_experiment_class
from app.db.models import ExperimentRun, ExperimentLog, Metric

logger = logging.getLogger(__name__)

settings = get_settings()

try:
    from celery import Celery
    _celery = Celery(
        "researchlab",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    _celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        worker_prefetch_multiplier=1,
        task_soft_time_limit=300,
        task_time_limit=600,
        task_acks_late=True,
    )

    @ _celery.task(bind=True, name="tasks.run_experiment")
    def run_experiment_task(self, run_id: str) -> dict:
        """Execute an experiment run inside a Celery worker."""
        import uuid as _uuid
        rid = _uuid.UUID(run_id)

        async def _run() -> dict:
            async with AsyncSessionLocal() as session:
                run = await session.get(ExperimentRun, rid)
                if not run:
                    raise ValueError(f"Run {rid} not found")

                from datetime import datetime, timezone
                now = datetime.now(tz=timezone.utc)
                run.started_at = now
                run.status = "RUNNING"
                run.worker_id = self.request.hostname or "unknown"
                await session.commit()

                log = ExperimentLog(
                    run_id=rid,
                    timestamp=now,
                    level="INFO",
                    message=f"Execution started on worker {run.worker_id}",
                )
                session.add(log)
                await session.flush()

                try:
                    exp_cls = get_experiment_class(run.configuration_snapshot.get("type", ""))
                    ctx = ExperimentContext(
                        config=run.configuration_snapshot,
                        random_seed=run.random_seed or 42,
                        experiment_id=str(run.experiment_id),
                        run_id=str(rid),
                    )

                    errors = exp_cls.validate_config(run.configuration_snapshot)
                    if errors:
                        raise ValueError(f"Validation failed: {'; '.join(errors)}")

                    results = exp_cls.execute(ctx)

                    completed_at = datetime.now(tz=timezone.utc)
                    duration = (completed_at - run.started_at).total_seconds()
                    run.status = "COMPLETED"
                    run.completed_at = completed_at
                    run.duration_seconds = duration
                    await session.commit()

                    for entry in ctx.logs:
                        from datetime import datetime, timezone as _tz
                        lg = ExperimentLog(
                            run_id=rid,
                            timestamp=datetime.fromtimestamp(entry["timestamp"], tz=_tz.utc),
                            level=entry["level"],
                            message=entry["message"],
                            metadata=entry.get("metadata"),
                        )
                        session.add(lg)
                    for m in ctx.metrics:
                        mt = Metric(
                            run_id=rid,
                            name=m["name"],
                            value=m["value"],
                            unit=m.get("unit"),
                            recorded_at=datetime.now(tz=__import__('datetime').timezone.utc),
                            step=m.get("step"),
                            metadata={"result_key": m.get("name")},
                        )
                        session.add(mt)
                    await session.commit()
                    return {"status": "completed", "results": results}

                except Exception as exc:
                    logger.exception("Run %s failed", rid)
                    from datetime import datetime, timezone
                    error_msg = str(exc)[:4000]
                    await session.execute(
                        ExperimentRun.__table__.update()
                        .where(ExperimentRun.id == rid)
                        .values(
                            status="FAILED",
                            completed_at=datetime.now(tz=timezone.utc),
                            error_message=error_msg,
                        )
                    )
                    await session.commit()
                    lg = ExperimentLog(
                        run_id=rid,
                        timestamp=datetime.now(tz=__import__('datetime').timezone.utc),
                        level="ERROR",
                        message=error_msg,
                    )
                    session.add(lg)
                    await session.commit()
                    return {"status": "failed", "error": error_msg}

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()

except ImportError:
    _celery = None
    run_experiment_task = None
    logger.warning("Celery not installed; background execution disabled.")
