"""Interfaz de drivers y utilidades de selección.

Operaciones tipadas, sin parámetros arbitrarios (ADR-007/ADR-008).
"""

from typing import Any, Protocol


class OperationsDriver(Protocol):
    mode: str

    def deploy_installation(self, spec: dict[str, Any]) -> dict[str, Any]: ...

    def upgrade_installation(self, spec: dict[str, Any]) -> dict[str, Any]: ...

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]: ...

    def health_check(self, installation_id: str) -> dict[str, Any]: ...

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]: ...

    def get_metrics(self, installation_id: str) -> dict[str, Any]: ...

    def request_backup(self, database_ref: str) -> dict[str, Any]: ...

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]: ...


def get_driver(mode: str) -> OperationsDriver:
    if mode == "real":
        from app.drivers.docker import RealDockerDriver

        return RealDockerDriver()
    from app.drivers.simulated import SimulatedDriver

    return SimulatedDriver()
