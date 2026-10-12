"""Utilidades de servicios."""

import uuid


def as_uuid(value: object) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError) as exc:
        raise LookupError("identificador inválido") from exc
