"""provisioning fields: eva image/port/health + installation host_port/container

Revision ID: 0005_provisioning
Revises: 0004_webauthn
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_provisioning"
down_revision: str | None = "0004_webauthn"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "eva_products", sa.Column("image_repo", sa.String(length=200), nullable=False, server_default="")
    )
    op.add_column(
        "eva_products", sa.Column("container_port", sa.Integer(), nullable=False, server_default="8000")
    )
    op.add_column(
        "eva_products",
        sa.Column("healthcheck_path", sa.String(length=120), nullable=False, server_default="/healthz"),
    )

    op.add_column("installations", sa.Column("host_port", sa.Integer(), nullable=True, unique=True))
    op.add_column(
        "installations", sa.Column("container_name", sa.String(length=160), nullable=False, server_default="")
    )


def downgrade() -> None:
    op.drop_column("installations", "container_name")
    op.drop_column("installations", "host_port")
    op.drop_column("eva_products", "healthcheck_path")
    op.drop_column("eva_products", "container_port")
    op.drop_column("eva_products", "image_repo")
