"""Endpoints de la API v1.

Módulos de identidad y comercial (Fase 3). Instalaciones sigue siendo un
esqueleto hasta la Fase 4.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    clients,
    evas,
    installations,
    plans,
    roles,
    subscriptions,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, tags=["roles"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(evas.router, prefix="/evas", tags=["evas"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(installations.router, prefix="/installations", tags=["installations"])
