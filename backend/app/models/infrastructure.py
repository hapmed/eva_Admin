"""Infraestructura: nodos, instalaciones, servicios, dominios, bases de datos,
configuración, referencias a secretos y operaciones tipadas.

Ninguna de estas entidades contiene credenciales: las bases de negocio se
referencian por metadatos y los secretos por su ubicación (`SECRET_REFERENCE`).
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import IdMixin, TimestampMixin


class Node(IdMixin, TimestampMixin, Base):
    __tablename__ = "nodes"

    name: Mapped[str] = mapped_column(String(120), unique=True)
    host_ref: Mapped[str] = mapped_column(String(160), default="")
    environment: Mapped[str] = mapped_column(String(20), default="prod")
    status: Mapped[str] = mapped_column(String(20), default="active")


class Installation(IdMixin, TimestampMixin, Base):
    __tablename__ = "installations"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    eva_product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eva_products.id"), index=True)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subscriptions.id"), nullable=True)
    node_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("nodes.id"), nullable=True)
    environment: Mapped[str] = mapped_column(String(20), default="prod")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    desired_version: Mapped[str] = mapped_column(String(40), default="")
    installed_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    last_operation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Aprovisionamiento real: puerto del host (solo 127.0.0.1) y nombre del contenedor.
    host_port: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True)
    container_name: Mapped[str] = mapped_column(String(160), default="")

    services: Mapped[list["InstallationService"]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )
    domains: Mapped[list["Domain"]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )


class InstallationService(IdMixin, TimestampMixin, Base):
    __tablename__ = "installation_services"
    __table_args__ = (UniqueConstraint("installation_id", "service_name", name="uq_installation_service"),)

    installation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installations.id", ondelete="CASCADE"), index=True
    )
    service_name: Mapped[str] = mapped_column(String(80))
    container_ref: Mapped[str] = mapped_column(String(160), default="")
    image_ref: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(20), default="unknown")
    health_status: Mapped[str] = mapped_column(String(20), default="unknown")
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    installation: Mapped[Installation] = relationship(back_populates="services")


class Domain(IdMixin, TimestampMixin, Base):
    __tablename__ = "domains"

    installation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installations.id", ondelete="CASCADE"), index=True
    )
    fqdn: Mapped[str] = mapped_column(String(253), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(20), default="primary")
    status: Mapped[str] = mapped_column(String(20), default="active")

    installation: Mapped[Installation] = relationship(back_populates="domains")


class DatabaseRecord(IdMixin, TimestampMixin, Base):
    __tablename__ = "database_records"

    installation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installations.id", ondelete="CASCADE"), index=True
    )
    engine: Mapped[str] = mapped_column(String(30), default="postgresql")
    logical_name: Mapped[str] = mapped_column(String(120))
    host_ref: Mapped[str] = mapped_column(String(160), default="")
    status: Mapped[str] = mapped_column(String(20), default="active")
    last_backup_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class InstallationConfig(IdMixin, TimestampMixin, Base):
    __tablename__ = "installation_configs"

    installation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installations.id", ondelete="CASCADE"), unique=True
    )
    config_json: Mapped[dict] = mapped_column(JSON, default=dict)
    schema_version: Mapped[str] = mapped_column(String(40), default="1")


class SecretReference(IdMixin, TimestampMixin, Base):
    __tablename__ = "secret_references"

    installation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installations.id", ondelete="CASCADE"), index=True
    )
    key: Mapped[str] = mapped_column(String(120))
    provider: Mapped[str] = mapped_column(String(60), default="env")
    path: Mapped[str] = mapped_column(String(200), default="")


class InstallationSecret(IdMixin, TimestampMixin, Base):
    """Valor de un secreto por instalación, **cifrado** (Fernet).

    El valor en claro nunca se guarda ni se registra; sólo se descifra para
    inyectarlo como variable de entorno en el despliegue.
    """

    __tablename__ = "installation_secrets"
    __table_args__ = (UniqueConstraint("installation_id", "key", name="uq_installation_secret"),)

    installation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installations.id", ondelete="CASCADE"), index=True
    )
    key: Mapped[str] = mapped_column(String(120))
    value_encrypted: Mapped[str] = mapped_column(Text)


class Operation(IdMixin, Base):
    __tablename__ = "operations"

    installation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("installations.id", ondelete="CASCADE"), index=True, nullable=True
    )
    type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="requested")
    requested_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result_summary: Mapped[str] = mapped_column(String(300), default="")
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
