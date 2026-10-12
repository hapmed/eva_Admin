"""Usuarios internos HAPMED (estructura; lógica en Fase 3)."""

from fastapi import APIRouter

from app.api.v1.endpoints._common import not_implemented

router = APIRouter()


@router.get("", summary="Listar usuarios internos")
def list_users() -> None:
    not_implemented()


@router.post("", summary="Crear usuario interno")
def create_user() -> None:
    not_implemented()
