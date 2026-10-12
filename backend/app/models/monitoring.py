"""Monitoreo: healthchecks, métricas, copias de seguridad y estado de alertas."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import IdMixin, TimestampMixin


class HealthCheck(IdMixin, Base):
    __tablename__ = "health_checks"

    installation_service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installation_services.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="unknown")
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Metric(IdMixin, Base):
    __tablename__ = "metrics"

    installation_service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("installation_services.id", ondelete="CASCADE"), index=True
    )
    metric_type: Mapped[str] = mapped_column(String(20))
    value: Mapped[float] = mapped_column(Float)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Backup(IdMixin, Base):
    __tablename__ = "backups"

    database_record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("database_records.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(20), default="full")
    status: Mapped[str] = mapped_column(String(20), default="simulated")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    location_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AlertState(IdMixin, TimestampMixin, Base):
    __tablename__ = "alert_states"

    key: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="open")
