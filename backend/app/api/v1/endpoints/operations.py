"""Consulta de operaciones (historial)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import operation_out
from app.db.session import get_db
from app.models.infrastructure import Operation
from app.schemas.installation import OperationOut
from app.services.util import as_uuid

router = APIRouter()


@router.get("", response_model=list[OperationOut])
def list_operations(
    installation_id: str | None = None,
    _: AuthContext = Depends(require_permission("operations:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    stmt = select(Operation).order_by(Operation.requested_at.desc())
    if installation_id:
        stmt = stmt.where(Operation.installation_id == as_uuid(installation_id))
    return [operation_out(operation) for operation in db.scalars(stmt).all()]


@router.get("/{operation_id}", response_model=OperationOut)
def get_operation(
    operation_id: str,
    _: AuthContext = Depends(require_permission("operations:read")),
    db: Session = Depends(get_db),
) -> dict:
    operation = db.get(Operation, as_uuid(operation_id))
    if operation is None:
        raise http_error(LookupError("operación no encontrada"))
    return operation_out(operation)
