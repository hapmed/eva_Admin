"""client slug (índice corto para dominio)

Revision ID: 0007_client_slug
Revises: 0006_eva_secrets
Create Date: 2026-10-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_client_slug"
down_revision: str | None = "0006_eva_secrets"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("slug", sa.String(length=30), nullable=True))
    op.create_index("ix_clients_slug", "clients", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_clients_slug", table_name="clients")
    op.drop_column("clients", "slug")
