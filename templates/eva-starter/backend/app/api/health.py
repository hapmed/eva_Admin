"""Endpoints de salud. `/healthz` se usa para confirmar despliegues."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/healthz", summary="Salud")
def healthz() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "version": settings.version}


@router.get("/readyz", summary="Readiness")
def readyz() -> dict[str, str]:
    return {"status": "ok"}
