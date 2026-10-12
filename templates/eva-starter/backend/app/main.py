"""Bootstrap de la aplicación FastAPI de la EVA."""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging("DEBUG" if settings.debug else "INFO")

    app = FastAPI(title=settings.app_name, version=settings.version)
    app.include_router(health_router)
    # Añade aquí tus routers: app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
