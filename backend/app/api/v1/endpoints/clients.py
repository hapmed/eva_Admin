"""Clientes y usuarios de cliente (estructura; lógica en Fase 3)."""

from fastapi import APIRouter

from app.api.v1.endpoints._common import not_implemented

router = APIRouter()


@router.get("", summary="Listar clientes")
def list_clients() -> None:
    not_implemented()


@router.post("", summary="Crear cliente")
def create_client() -> None:
    not_implemented()
