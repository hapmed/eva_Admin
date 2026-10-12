"""API tokens (acceso máquina-a-máquina) para integraciones y el agente."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import IdMixin, TimestampMixin


class ApiToken(IdMixin, TimestampMixin, Base):
    __tablename__ = "api_tokens"

    name: Mapped[str] = mapped_column(String(120))
    owner_type: Mapped[str] = mapped_column(String(20), default="integration", nullable=False)
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list)
    token_hash: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
