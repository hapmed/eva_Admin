"""Clientes y usuarios de cliente (esqueleto inicial).

Los datos de negocio de cada cliente viven en su propia base (ADR-012); esta
entidad sólo representa los metadatos en la base administrativa.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import IdMixin, TimestampMixin


class Client(IdMixin, TimestampMixin, Base):
    __tablename__ = "clients"

    legal_name: Mapped[str] = mapped_column(String(200))
    display_name: Mapped[str] = mapped_column(String(200))
    tax_id: Mapped[str | None] = mapped_column(String(60), nullable=True)
    # Índice corto único para el subdominio inicial (derivado del RFC).
    slug: Mapped[str | None] = mapped_column(String(30), unique=True, index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    notes: Mapped[str] = mapped_column(String(500), default="")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    users: Mapped[list["ClientUser"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class ClientUser(IdMixin, TimestampMixin, Base):
    __tablename__ = "client_users"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role_code: Mapped[str] = mapped_column(String(64), default="client_viewer", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    client: Mapped[Client] = relationship(back_populates="users")
