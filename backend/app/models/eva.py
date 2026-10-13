"""Catálogo de aplicaciones EVA y sus versiones."""

import uuid

from sqlalchemy import JSON, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import IdMixin, TimestampMixin


class EvaProduct(IdMixin, TimestampMixin, Base):
    __tablename__ = "eva_products"

    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    # Esquema de configuración permitido (props/requeridos). Nunca secretos.
    config_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    # Despliegue: repositorio de imagen, puerto interno y ruta de salud.
    image_repo: Mapped[str] = mapped_column(String(200), default="")
    container_port: Mapped[int] = mapped_column(Integer, default=8000)
    healthcheck_path: Mapped[str] = mapped_column(String(120), default="/healthz")
    # Comando de migración idempotente (p. ej. "alembic upgrade head").
    migrate_command: Mapped[str] = mapped_column(String(300), default="")

    versions: Mapped[list["EvaVersion"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class EvaVersion(IdMixin, TimestampMixin, Base):
    __tablename__ = "eva_versions"
    __table_args__ = (UniqueConstraint("eva_product_id", "version", name="uq_eva_version"),)

    eva_product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("eva_products.id", ondelete="CASCADE"), index=True
    )
    version: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="approved", nullable=False)
    deployment_requirements: Mapped[dict] = mapped_column(JSON, default=dict)

    product: Mapped[EvaProduct] = relationship(back_populates="versions")
