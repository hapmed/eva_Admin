"""Configuración pública para el frontend (branding)."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["config"])


@router.get("/config", summary="Configuración pública")
def public_config() -> dict[str, str]:
    settings = get_settings()
    return {
        "client_name": settings.client_name,
        "app_name": settings.app_name,
        "version": settings.version,
    }
