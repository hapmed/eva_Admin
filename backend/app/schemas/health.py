"""Respuestas de salud y readiness (sin secretos)."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ReadyCheck(BaseModel):
    name: str
    status: str


class ReadyResponse(BaseModel):
    status: str
    checks: list[ReadyCheck]
