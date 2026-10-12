"""Operaciones tipadas: registro, idempotencia y llamada al agente."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.client import get_agent
from app.core.auth import AuthContext
from app.models.infrastructure import Operation
from app.services import audit
from app.services.util import as_uuid


def existing_by_key(db: Session, idempotency_key: str | None) -> Operation | None:
    if not idempotency_key:
        return None
    return db.scalar(select(Operation).where(Operation.idempotency_key == idempotency_key))


def run(
    db: Session,
    context: AuthContext,
    installation_id: str | None,
    operation_type: str,
    *,
    idempotency_key: str | None = None,
    call=None,
    summary: str = "",
) -> Operation:
    """Ejecuta (o recupera por idempotencia) una operación tipada.

    `call` es un callable que invoca al agente y devuelve su resultado (dict).
    """
    existing = existing_by_key(db, idempotency_key)
    if existing is not None:
        return existing

    agent = get_agent()
    operation = Operation(
        installation_id=as_uuid(installation_id) if installation_id else None,
        type=operation_type,
        status="running",
        requested_by=context.actor_id,
        requested_at=datetime.now(UTC),
        idempotency_key=idempotency_key,
    )
    db.add(operation)
    db.flush()

    result: dict = {}
    try:
        result = call(agent) if call is not None else {}
        operation.status = "succeeded"
    except Exception:  # noqa: BLE001 - se reporta un código genérico, sin detalles
        operation.status = "failed"
        operation.error_code = "agent_error"

    operation.result_json = result
    operation.simulated = bool(result.get("simulated", agent.mode != "real"))
    operation.result_summary = summary
    operation.finished_at = datetime.now(UTC)

    audit.record(
        db,
        context,
        f"operation.{operation_type}",
        "operation",
        operation.id,
        installation_id=installation_id or "",
        simulated=operation.simulated,
    )
    return operation
