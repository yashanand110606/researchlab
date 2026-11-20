"""SQLAlchemy 2.x ORM models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    configuration: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    configuration_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now, nullable=False)

    runs: Mapped[list["ExperimentRun"]] = relationship(back_populates="experiment", lazy="selectin")
    tags: Mapped[list["ExperimentTag"]] = relationship(back_populates="experiment", lazy="selectin")

    __table_args__ = (
        Index("ix_experiments_category", "category"),
        Index("ix_experiments_created_at", "created_at"),
    )


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    configuration_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    random_seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    worker_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)

    experiment: Mapped["Experiment"] = relationship(back_populates="runs")
    metrics: Mapped[list["Metric"]] = relationship(back_populates="run", lazy="selectin")
    logs: Mapped[list["ExperimentLog"]] = relationship(back_populates="run", lazy="selectin")

    __table_args__ = (
        Index("ix_experiment_runs_experiment_id", "experiment_id"),
        Index("ix_experiment_runs_status", "status"),
        Index("ix_experiment_runs_created_at", "created_at"),
    )


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Integer, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)
    step: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True, name="metadata")

    run: Mapped["ExperimentRun"] = relationship(back_populates="metrics")

    __table_args__ = (
        Index("ix_metrics_run_id", "run_id"),
        Index("ix_metrics_name", "name"),
        Index("ix_metrics_recorded_at", "recorded_at"),
    )


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_format: Mapped[str] = mapped_column(String(50), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)

    __table_args__ = (
        Index("ix_datasets_filename", "filename"),
        Index("ix_datasets_created_at", "created_at"),
    )


class ExperimentTag(Base):
    __tablename__ = "experiment_tags"
    __table_args__ = (
        UniqueConstraint("experiment_id", "tag", name="uq_experiment_tag"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_now, nullable=False)

    experiment: Mapped["Experiment"] = relationship(back_populates="tags")

    __table_args__ = (Index("ix_experiment_tags_experiment_id", "experiment_id"),)


class ExperimentLog(Base):
    __tablename__ = "experiment_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(default=_now, nullable=False)
    level: Mapped[str] = mapped_column(String(10), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True, name="metadata")

    run: Mapped["ExperimentRun"] = relationship(back_populates="logs")

    __table_args__ = (
        Index("ix_experiment_logs_run_id", "run_id"),
        Index("ix_experiment_logs_timestamp", "timestamp"),
    )
