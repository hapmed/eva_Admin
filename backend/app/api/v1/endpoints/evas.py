"""Catálogo de aplicaciones EVA (estructura; lógica en Fase 3)."""

from fastapi import APIRouter

from app.api.v1.endpoints._common import not_implemented

router = APIRouter()


@router.get("", summary="Listar EVA")
def list_evas() -> None:
    not_implemented()


@router.post("", summary="Crear EVA")
def create_eva() -> None:
    not_implemented()
