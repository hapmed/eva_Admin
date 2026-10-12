"""Utilidades compartidas por los endpoints del esqueleto."""

from fastapi import HTTPException, status


def not_implemented() -> None:
    """Respuesta honesta para endpoints todavía no implementados."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Pendiente: se implementa en una fase posterior.",
    )
