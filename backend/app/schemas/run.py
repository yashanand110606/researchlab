"""Pydantic v2 schemas for experiment runs."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


VALID_RUN_STATUSES = {"PENDING", "QUEUED", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"}
VALID_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"QUEUED", "CANCELLED"},
    "QUEUED": {"RUNNING", "CANCELLED"},
    "RUNNING": {"COMPLETED", "FAILED", "CANCELLED"},
    "COMPLETED": set(),
    "FAILED": {"QUEUED"},
    "CANCELLED": {"QUEUED"},
}


class RunCreateRequest(BaseModel):
    random_seed: Optional[int] = None


class RunOut(BaseModel):
    id: UUID
    experiment_id: UUID
    status: str
    configuration_snapshot: dict[str, Any]
    random_seed: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]
    worker_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RunCancelRequest(BaseModel):
    force: bool = False


class MetricOut(BaseModel):
    id: UUID
    run_id: UUID
    name: str
    value: float
    unit: Optional[str]
    recorded_at: datetime
    step: Optional[int]
    metadata: Optional[dict[str, Any]]

    class Config:
        from_attributes = True


class LogEntry(BaseModel):
    id: UUID
    run_id: UUID
    timestamp: datetime
    level: str
    message: str
    metadata: Optional[dict[str, Any]]

    class Config:
        from_attributes = True
