"""eva migrate_command + per-installation encrypted secrets

Revision ID: 0006_eva_secrets
Revises: 0005_provisioning
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_eva_secrets"
down_revision: str | None = "0005_provisioning"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "eva_products",
        sa.Column("migrate_command", sa.String(length=300), nullable=False, server_default=""),
    )

    op.create_table(
        "installation_secrets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "installation_id",
            sa.Uuid(),
            sa.ForeignKey("installations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value_encrypted", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("installation_id", "key", name="uq_installation_secret"),
    )
    op.create_index("ix_installation_secrets_installation_id", "installation_secrets", ["installation_id"])


def downgrade() -> None:
    op.drop_index("ix_installation_secrets_installation_id", table_name="installation_secrets")
    op.drop_table("installation_secrets")
    op.drop_column("eva_products", "migrate_command")
