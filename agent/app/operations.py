"""Operaciones tipadas del agente.

Cada operación define parámetros permitidos y requeridos. Se rechaza cualquier
parámetro no declarado (sin imágenes, puertos, montajes ni privilegios).
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.drivers.base import OperationsDriver, get_driver

_DEPLOY_PARAMS = {
    "image",
    "name",
    "network",
    "host_port",
    "container_port",
    "env",
    "labels",
    "migrate",
}


class OperationType(StrEnum):
    deploy_installation = "deploy_installation"
    upgrade_installation = "upgrade_installation"
    restart_service = "restart_service"
    health_check = "health_check"
    get_logs = "get_logs"
    get_metrics = "get_metrics"
    request_backup = "request_backup"
    request_restore = "request_restore"


class OperationRequest(BaseModel):
    type: OperationType
    installation_id: str = ""
    params: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None


class OperationResult(BaseModel):
    type: str
    status: str
    simulated: bool
    data: dict[str, Any] = Field(default_factory=dict)


ALLOWED_PARAMS: dict[OperationType, set[str]] = {
    OperationType.deploy_installation: _DEPLOY_PARAMS,
    OperationType.upgrade_installation: _DEPLOY_PARAMS,
    OperationType.restart_service: {"service_name"},
    OperationType.health_check: set(),
    OperationType.get_logs: {"limit"},
    OperationType.get_metrics: set(),
    OperationType.request_backup: {"database_ref"},
    OperationType.request_restore: {"database_ref", "backup_ref"},
}

REQUIRED_PARAMS: dict[OperationType, set[str]] = {
    OperationType.deploy_installation: {"image", "name", "host_port"},
    OperationType.upgrade_installation: {"image", "name", "host_port"},
    OperationType.restart_service: {"service_name"},
    OperationType.health_check: set(),
    OperationType.get_logs: set(),
    OperationType.get_metrics: set(),
    OperationType.request_backup: {"database_ref"},
    OperationType.request_restore: {"database_ref", "backup_ref"},
}


def validate_params(request: OperationRequest) -> None:
    allowed = ALLOWED_PARAMS[request.type]
    required = REQUIRED_PARAMS[request.type]

    extra = set(request.params) - allowed
    if extra:
        raise ValueError(f"parámetros no permitidos: {', '.join(sorted(extra))}")

    missing = [name for name in required if not request.params.get(name)]
    if missing:
        raise ValueError(f"faltan parámetros: {', '.join(sorted(missing))}")


def _dispatch(driver: OperationsDriver, request: OperationRequest) -> dict[str, Any]:
    params = request.params
    if request.type is OperationType.deploy_installation:
        return driver.deploy_installation(params)
    if request.type is OperationType.upgrade_installation:
        return driver.upgrade_installation(params)
    if request.type is OperationType.restart_service:
        return driver.restart_service(request.installation_id, params["service_name"])
    if request.type is OperationType.health_check:
        return driver.health_check(request.installation_id)
    if request.type is OperationType.get_logs:
        return driver.get_logs(request.installation_id, int(params.get("limit", 200)))
    if request.type is OperationType.get_metrics:
        return driver.get_metrics(request.installation_id)
    if request.type is OperationType.request_backup:
        return driver.request_backup(params["database_ref"])
    if request.type is OperationType.request_restore:
        return driver.request_restore(params["database_ref"], params["backup_ref"])
    raise ValueError("operación desconocida")


def execute(request: OperationRequest, mode: str) -> OperationResult:
    validate_params(request)
    driver = get_driver(mode)
    data = _dispatch(driver, request)
    return OperationResult(
        type=request.type.value,
        status="accepted",
        simulated=driver.mode != "real",
        data=data,
    )
