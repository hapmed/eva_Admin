"""Metadatos de bases de datos asignadas (sin credenciales)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import database_out, operation_out
from app.db.session import get_db
from app.schemas.installation import (
    DatabaseCreate,
    DatabaseOut,
    OperationOut,
    OperationRequest,
    RestoreRequest,
)
from app.services import database_service

router = APIRouter()


@router.get("", response_model=list[DatabaseOut])
def list_databases(
    installation_id: str | None = None,
    _: AuthContext = Depends(require_permission("databases:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    return [database_out(record) for record in database_service.list_databases(db, installation_id)]


@router.post("", response_model=DatabaseOut, status_code=201)
def create_database(
    data: DatabaseCreate,
    context: AuthContext = Depends(require_permission("databases:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        record = database_service.create_database(
            db, context, data.installation_id, data.engine, data.logical_name, data.host_ref
        )
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return database_out(record)


@router.get("/{database_id}", response_model=DatabaseOut)
def get_database(
    database_id: str,
    _: AuthContext = Depends(require_permission("databases:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        record = database_service.get_database(db, database_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return database_out(record)


@router.post("/{database_id}/backup", response_model=OperationOut)
def backup_database(
    database_id: str,
    data: OperationRequest,
    context: AuthContext = Depends(require_permission("backups:request")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        operation = database_service.request_backup(db, context, database_id, data.idempotency_key)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return operation_out(operation)


@router.post("/{database_id}/restore", response_model=OperationOut)
def restore_database(
    database_id: str,
    data: RestoreRequest,
    context: AuthContext = Depends(require_permission("backups:restore")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        operation = database_service.request_restore(
            db, context, database_id, data.backup_ref, data.idempotency_key
        )
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return operation_out(operation)
