"""Planes y suscripciones (estructura; lógica en Fase 3)."""

from fastapi import APIRouter

from app.api.v1.endpoints._common import not_implemented

router = APIRouter()


@router.get("", summary="Listar suscripciones")
def list_subscriptions() -> None:
    not_implemented()


@router.post("", summary="Crear suscripción")
def create_subscription() -> None:
    not_implemented()
