"""Instalaciones (estructura; lógica en Fase 4)."""

from fastapi import APIRouter

from app.api.v1.endpoints._common import not_implemented

router = APIRouter()


@router.get("", summary="Listar instalaciones")
def list_installations() -> None:
    not_implemented()


@router.post("", summary="Crear instalación")
def create_installation() -> None:
    not_implemented()
