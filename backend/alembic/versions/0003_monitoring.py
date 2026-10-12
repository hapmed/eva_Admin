"""monitoring: healthchecks, metrics, backups, alert states

Revision ID: 0003_monitoring
Revises: 0002_provisioning
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_monitoring"
down_revision: str | None = "0002_provisioning"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "health_checks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_service_id",
            sa.Uuid(),
            sa.ForeignKey("installation_services.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_health_checks_installation_service_id", "health_checks", ["installation_service_id"])

    op.create_table(
        "metrics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_service_id",
            sa.Uuid(),
            sa.ForeignKey("installation_services.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metric_type", sa.String(length=20), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_metrics_installation_service_id", "metrics", ["installation_service_id"])

    op.create_table(
        "backups",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "database_record_id",
            sa.Uuid(),
            sa.ForeignKey("database_records.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location_ref", sa.String(length=200), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
    )
    op.create_index("ix_backups_database_record_id", "backups", ["database_record_id"])

    op.create_table(
        "alert_states",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("key", sa.String(length=200), nullable=False, unique=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_alert_states_key", "alert_states", ["key"])


def downgrade() -> None:
    for table in ("alert_states", "backups", "metrics", "health_checks"):
        op.drop_table(table)
