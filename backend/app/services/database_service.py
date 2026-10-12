"""Metadatos de bases de datos asignadas a instalaciones.

Nunca se guardan ni se devuelven credenciales; sólo metadatos.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.models.infrastructure import DatabaseRecord
from app.services import audit, installation_service, operations
from app.services.util import as_uuid


def list_databases(db: Session, installation_id: str | None = None) -> list[DatabaseRecord]:
    stmt = select(DatabaseRecord).order_by(DatabaseRecord.logical_name)
    if installation_id:
        stmt = stmt.where(DatabaseRecord.installation_id == as_uuid(installation_id))
    return list(db.scalars(stmt).all())


def get_database(db: Session, database_id: str) -> DatabaseRecord:
    record = db.get(DatabaseRecord, as_uuid(database_id))
    if record is None:
        raise LookupError("base de datos no encontrada")
    return record


def create_database(
    db: Session,
    context: AuthContext,
    installation_id: str,
    engine: str,
    logical_name: str,
    host_ref: str,
) -> DatabaseRecord:
    installation = installation_service.get_installation(db, installation_id)
    record = DatabaseRecord(
        installation_id=installation.id,
        engine=engine,
        logical_name=logical_name,
        host_ref=host_ref,
        status="active",
    )
    db.add(record)
    db.flush()
    audit.record(db, context, "database.create", "database_record", record.id, logical_name=logical_name)
    db.commit()
    db.refresh(record)
    return record


def request_backup(db: Session, context: AuthContext, database_id: str, idempotency_key: str | None = None):
    record = get_database(db, database_id)
    operation = operations.run(
        db,
        context,
        str(record.installation_id),
        "request_backup",
        idempotency_key=idempotency_key,
        call=lambda agent: agent.request_backup(record.logical_name),
        summary="copia de seguridad solicitada (simulada)",
    )
    if not operation.simulated:
        record.last_backup_at = datetime.now(UTC)
    db.commit()
    return operation


def request_restore(
    db: Session,
    context: AuthContext,
    database_id: str,
    backup_ref: str,
    idempotency_key: str | None = None,
):
    record = get_database(db, database_id)
    operation = operations.run(
        db,
        context,
        str(record.installation_id),
        "request_restore",
        idempotency_key=idempotency_key,
        call=lambda agent: agent.request_restore(record.logical_name, backup_ref),
        summary="restauración solicitada (simulada)",
    )
    db.commit()
    return operation
