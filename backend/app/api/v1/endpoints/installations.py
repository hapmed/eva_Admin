"""Instalaciones, servicios y operaciones de ciclo de vida."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import installation_out, operation_out, service_out
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.schemas.eva_user import EvaUserCreate, EvaUserOut, EvaUserReset
from app.schemas.installation import (
    InstallationCreate,
    InstallationOut,
    InstallationServiceOut,
    InstallationUpdate,
    OperationOut,
    RestartRequest,
    UpgradeRequest,
)
from app.schemas.monitoring import LogsOut, MetricsOut
from app.services import eva_users, installation_service, monitoring_service

router = APIRouter()


def _out(db: Session, installation) -> dict:
    secrets = installation_service.list_secrets(db, str(installation.id))
    return installation_out(installation, secrets)


@router.get("", response_model=list[InstallationOut])
def list_installations(
    client_id: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    _: AuthContext = Depends(require_permission("installations:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    installations = installation_service.list_installations(db, client_id, status_filter)
    return [_out(db, installation) for installation in installations]


@router.post(
    "", response_model=InstallationOut, status_code=201, dependencies=[Depends(rate_limit("operations"))]
)
def create_installation(
    data: InstallationCreate,
    context: AuthContext = Depends(require_permission("installations:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        installation = installation_service.create_installation(db, context, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return _out(db, installation)


@router.get("/{installation_id}", response_model=InstallationOut)
def get_installation(
    installation_id: str,
    _: AuthContext = Depends(require_permission("installations:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        installation = installation_service.get_installation(db, installation_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return _out(db, installation)


@router.patch("/{installation_id}", response_model=InstallationOut)
def update_installation(
    installation_id: str,
    data: InstallationUpdate,
    context: AuthContext = Depends(require_permission("installations:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        installation = installation_service.update_installation(db, context, installation_id, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return _out(db, installation)


@router.get("/{installation_id}/services", response_model=list[InstallationServiceOut])
def list_services(
    installation_id: str,
    _: AuthContext = Depends(require_permission("installations:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    try:
        installation = installation_service.get_installation(db, installation_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return [service_out(service) for service in installation.services]


@router.get("/{installation_id}/health")
def get_health(
    installation_id: str,
    _: AuthContext = Depends(require_permission("installations:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        installation = installation_service.get_installation(db, installation_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return {
        "status": installation.status,
        "services": [service_out(service) for service in installation.services],
    }


@router.get("/{installation_id}/logs", response_model=LogsOut)
def get_logs(
    installation_id: str,
    _: AuthContext = Depends(require_permission("operations:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        installation = installation_service.get_installation(db, installation_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return monitoring_service.get_logs(installation)


@router.get("/{installation_id}/metrics", response_model=MetricsOut)
def get_metrics(
    installation_id: str,
    _: AuthContext = Depends(require_permission("operations:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        installation = installation_service.get_installation(db, installation_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return monitoring_service.get_metrics(installation)


@router.post(
    "/{installation_id}/restart",
    response_model=OperationOut,
    dependencies=[Depends(rate_limit("operations"))],
)
def restart_service(
    installation_id: str,
    data: RestartRequest,
    context: AuthContext = Depends(require_permission("installations:operate")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        operation = installation_service.restart(
            db, context, installation_id, data.service_name, data.idempotency_key
        )
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return operation_out(operation)


@router.post(
    "/{installation_id}/upgrade",
    response_model=OperationOut,
    dependencies=[Depends(rate_limit("operations"))],
)
def upgrade_installation(
    installation_id: str,
    data: UpgradeRequest,
    context: AuthContext = Depends(require_permission("installations:upgrade")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        _, operation = installation_service.upgrade(
            db, context, installation_id, data.target_version, data.idempotency_key
        )
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return operation_out(operation)


@router.post(
    "/{installation_id}/health-check",
    response_model=OperationOut,
    dependencies=[Depends(rate_limit("operations"))],
)
def run_health_check(
    installation_id: str,
    context: AuthContext = Depends(require_permission("installations:operate")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        operation = installation_service.health_check(db, context, installation_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return operation_out(operation)


@router.get("/{installation_id}/users", response_model=list[EvaUserOut])
def list_eva_users(
    installation_id: str,
    _: AuthContext = Depends(require_permission("installations:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    try:
        return eva_users.list_users(db, installation_id)
    except (ValueError, LookupError, RuntimeError) as exc:
        raise http_error(exc) from exc


@router.post("/{installation_id}/users", response_model=EvaUserOut, status_code=201)
def create_eva_user(
    installation_id: str,
    data: EvaUserCreate,
    context: AuthContext = Depends(require_permission("installations:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return eva_users.create_user(
            db, context, installation_id, data.email, data.password, data.full_name, data.role
        )
    except (ValueError, LookupError, RuntimeError) as exc:
        raise http_error(exc) from exc


@router.post("/{installation_id}/users/{user_id}/reset-password", status_code=204)
def reset_eva_user_password(
    installation_id: str,
    user_id: str,
    data: EvaUserReset,
    context: AuthContext = Depends(require_permission("installations:write")),
    db: Session = Depends(get_db),
) -> None:
    try:
        eva_users.reset_password(db, context, installation_id, user_id, data.password)
    except (ValueError, LookupError, RuntimeError) as exc:
        raise http_error(exc) from exc


@router.delete("/{installation_id}/users/{user_id}", status_code=204)
def delete_eva_user(
    installation_id: str,
    user_id: str,
    context: AuthContext = Depends(require_permission("installations:write")),
    db: Session = Depends(get_db),
) -> None:
    try:
        eva_users.delete_user(db, context, installation_id, user_id)
    except (ValueError, LookupError, RuntimeError) as exc:
        raise http_error(exc) from exc
