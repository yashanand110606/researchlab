"""Initial Alembic migration — create all tables."""
"""initial_models
Revision ID: initial_models
Create Date: 2026-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "initial_models"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=False, server_default="general"),
        sa.Column("configuration", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("configuration_version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_experiments_category", "experiments", ["category"])
    op.create_index("ix_experiments_created_at", "experiments", ["created_at"])

    op.create_table(
        "datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("file_format", sa.String(50), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_datasets_filename", "datasets", ["filename"])
    op.create_index("ix_datasets_created_at", "datasets", ["created_at"])

    op.create_table(
        "experiment_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("configuration_snapshot", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("random_seed", sa.Integer, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("worker_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_experiment_runs_experiment_id", "experiment_runs", ["experiment_id"])
    op.create_index("ix_experiment_runs_status", "experiment_runs", ["status"])
    op.create_index("ix_experiment_runs_created_at", "experiment_runs", ["created_at"])

    op.create_table(
        "metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("step", sa.Integer, nullable=True),
        sa.Column("metadata_", postgresql.JSONB, nullable=True),
    )
    op.create_index("ix_metrics_run_id", "metrics", ["run_id"])
    op.create_index("ix_metrics_name", "metrics", ["name"])
    op.create_index("ix_metrics_recorded_at", "metrics", ["recorded_at"])

    op.create_table(
        "experiment_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("experiment_id", "tag", name="uq_experiment_tag"),
    )
    op.create_index("ix_experiment_tags_experiment_id", "experiment_tags", ["experiment_id"])

    op.create_table(
        "experiment_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("level", sa.String(10), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("metadata_", postgresql.JSONB, nullable=True),
    )
    op.create_index("ix_experiment_logs_run_id", "experiment_logs", ["run_id"])
    op.create_index("ix_experiment_logs_timestamp", "experiment_logs", ["timestamp"])


def downgrade() -> None:
    op.drop_table("experiment_logs")
    op.drop_table("experiment_tags")
    op.drop_table("metrics")
    op.drop_table("experiment_runs")
    op.drop_table("datasets")
    op.drop_table("experiments")
