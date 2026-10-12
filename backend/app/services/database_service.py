"""Metadatos de bases de datos asignadas a instalaciones.

Nunca se guardan ni se devuelven credenciales; sólo metadatos.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.models.infrastructure import DatabaseRecord
from app.models.monitoring import Backup
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


def list_backups(db: Session, database_id: str) -> list[Backup]:
    record = get_database(db, database_id)
    return list(
        db.scalars(
            select(Backup).where(Backup.database_record_id == record.id).order_by(Backup.started_at.desc())
        ).all()
    )


def request_backup(db: Session, context: AuthContext, database_id: str, idempotency_key: str | None = None):
    record = get_database(db, database_id)
    operation = operations.run(
        db,
        context,
        str(record.installation_id),
        "request_backup",
        idempotency_key=idempotency_key,
        call=lambda agent: agent.request_backup(record.logical_name),
        summary="copia de seguridad",
    )
    data = operation.result_json or {}
    now = datetime.now(UTC)
    if operation.status == "succeeded":
        status = "simulated" if operation.simulated else "succeeded"
    else:
        status = "failed"
    db.add(
        Backup(
            database_record_id=record.id,
            type="full",
            status=status,
            started_at=now,
            finished_at=now,
            location_ref=data.get("location_ref"),
            size_bytes=data.get("size_bytes"),
        )
    )
    if status == "succeeded":
        record.last_backup_at = now
    audit.record(db, context, "database.backup", "database_record", record.id, status=status)
    db.commit()
    return operation


def request_restore(
    db: Session,
    context: AuthContext,
    database_id: str,
    backup_id: str,
    idempotency_key: str | None = None,
    confirm: str = "",
):
    record = get_database(db, database_id)
    if confirm.strip() != record.logical_name:
        raise ValueError("confirmación incorrecta: escribe el nombre de la base de datos")
    backup = db.get(Backup, as_uuid(backup_id))
    if backup is None or backup.database_record_id != record.id:
        raise LookupError("copia de seguridad no encontrada")
    if not backup.location_ref:
        raise ValueError("esa copia no tiene fichero asociado")

    operation = operations.run(
        db,
        context,
        str(record.installation_id),
        "request_restore",
        idempotency_key=idempotency_key,
        call=lambda agent: agent.request_restore(record.logical_name, backup.location_ref),
        summary="restauración de base de datos",
    )
    audit.record(db, context, "database.restore", "database_record", record.id, backup_ref=backup_id)
    db.commit()
    return operation
