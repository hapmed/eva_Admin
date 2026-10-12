"""Autenticación (estructura; lógica en Fase 3).

Auth dual (ADR-009): cookie de sesión para la SPA + token Bearer para
integraciones/agente.
"""

from fastapi import APIRouter

from app.api.v1.endpoints._common import not_implemented

router = APIRouter()


@router.get("/csrf", summary="Obtener token CSRF")
def get_csrf() -> None:
    not_implemented()


@router.post("/login", summary="Iniciar sesión")
def login() -> None:
    not_implemented()


@router.post("/logout", summary="Cerrar sesión")
def logout() -> None:
    not_implemented()


@router.get("/me", summary="Usuario actual y permisos")
def me() -> None:
    not_implemented()
