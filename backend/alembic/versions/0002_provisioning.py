"""provisioning entities

Revision ID: 0002_provisioning
Revises: 0001_initial
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_provisioning"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("eva_products", sa.Column("config_schema", sa.JSON(), nullable=False, server_default="{}"))

    op.create_table(
        "nodes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("host_ref", sa.String(length=160), nullable=False),
        sa.Column("environment", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "installations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("client_id", sa.Uuid(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("eva_product_id", sa.Uuid(), sa.ForeignKey("eva_products.id"), nullable=False),
        sa.Column("subscription_id", sa.Uuid(), sa.ForeignKey("subscriptions.id"), nullable=True),
        sa.Column("node_id", sa.Uuid(), sa.ForeignKey("nodes.id"), nullable=True),
        sa.Column("environment", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("desired_version", sa.String(length=40), nullable=False),
        sa.Column("installed_version", sa.String(length=40), nullable=True),
        sa.Column("last_operation_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_installations_client_id", "installations", ["client_id"])
    op.create_index("ix_installations_eva_product_id", "installations", ["eva_product_id"])

    op.create_table(
        "installation_services",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_id",
            sa.Uuid(),
            sa.ForeignKey("installations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("service_name", sa.String(length=80), nullable=False),
        sa.Column("container_ref", sa.String(length=160), nullable=False),
        sa.Column("image_ref", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("health_status", sa.String(length=20), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("installation_id", "service_name", name="uq_installation_service"),
    )
    op.create_index("ix_installation_services_installation_id", "installation_services", ["installation_id"])

    op.create_table(
        "domains",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_id",
            sa.Uuid(),
            sa.ForeignKey("installations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("fqdn", sa.String(length=253), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("fqdn"),
    )
    op.create_index("ix_domains_installation_id", "domains", ["installation_id"])
    op.create_index("ix_domains_fqdn", "domains", ["fqdn"])

    op.create_table(
        "database_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_id",
            sa.Uuid(),
            sa.ForeignKey("installations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("engine", sa.String(length=30), nullable=False),
        sa.Column("logical_name", sa.String(length=120), nullable=False),
        sa.Column("host_ref", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("last_backup_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_database_records_installation_id", "database_records", ["installation_id"])

    op.create_table(
        "installation_configs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_id",
            sa.Uuid(),
            sa.ForeignKey("installations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("schema_version", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "secret_references",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_id",
            sa.Uuid(),
            sa.ForeignKey("installations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=60), nullable=False),
        sa.Column("path", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_secret_references_installation_id", "secret_references", ["installation_id"])

    op.create_table(
        "operations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_id", sa.Uuid(), sa.ForeignKey("installations.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("requested_by", sa.String(length=64), nullable=True),
        sa.Column(
            "requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_summary", sa.String(length=300), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("error_code", sa.String(length=60), nullable=True),
        sa.Column("idempotency_key", sa.String(length=120), nullable=True),
        sa.Column("simulated", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_operations_installation_id", "operations", ["installation_id"])


def downgrade() -> None:
    for table in (
        "operations",
        "secret_references",
        "installation_configs",
        "database_records",
        "domains",
        "installation_services",
        "installations",
        "nodes",
    ):
        op.drop_table(table)
    op.drop_column("eva_products", "config_schema")
