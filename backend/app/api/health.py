"""Endpoints de salud (liveness y readiness). No exponen secretos."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse, ReadyCheck, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse, summary="Liveness")
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/readyz", response_model=ReadyResponse, summary="Readiness")
def readyz() -> ReadyResponse:
    """Comprueba configuración y estado del agente.

    Fase 2 no abre conexión a la base de datos: el chequeo `database` aparece
    como `not_checked`. No se filtran hosts, usuarios ni credenciales.
    """
    settings = get_settings()
    checks = [
        ReadyCheck(name="config", status="ok"),
        ReadyCheck(name="database", status="not_checked"),
        ReadyCheck(name="agent", status=settings.agent_mode),
    ]
    overall = "ok" if all(check.status != "error" for check in checks) else "degraded"
    return ReadyResponse(status=overall, checks=checks)
