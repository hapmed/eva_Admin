"""Registro de auditoría."""

from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.models.audit import AuditLog


def record(
    db: Session,
    context: AuthContext,
    action: str,
    entity_type: str,
    entity_id: object | None = None,
    **metadata: object,
) -> None:
    db.add(
        AuditLog(
            actor_type=context.actor_type,
            actor_id=context.actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            metadata_json={key: str(value) for key, value in metadata.items()},
        )
    )
