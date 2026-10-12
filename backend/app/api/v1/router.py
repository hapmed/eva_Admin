"""Endpoints de la API v1.

En Fase 2 sólo se define la estructura modular (routers por dominio) con
respuestas `501 Not Implemented`. La lógica de dominio llega en fases 3-5.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, clients, evas, installations, subscriptions, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(evas.router, prefix="/evas", tags=["evas"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(installations.router, prefix="/installations", tags=["installations"])
