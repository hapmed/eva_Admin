"""Cliente del agente de operaciones.

Interfaz tipada hacia el agente (ADR-007). En esta fase sólo existe el adaptador
`SimulatedAgent`, que NO realiza cambios reales.
"""

from typing import Any, Protocol


class OperationsAgent(Protocol):
    """Operaciones tipadas del agente. Sin parámetros arbitrarios."""

    mode: str

    def deploy_installation(
        self, installation_id: str, eva_version: str, domain: str | None
    ) -> dict[str, Any]: ...

    def upgrade_installation(self, installation_id: str, target_version: str) -> dict[str, Any]: ...

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]: ...

    def health_check(self, installation_id: str) -> dict[str, Any]: ...

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]: ...

    def get_metrics(self, installation_id: str) -> dict[str, Any]: ...

    def request_backup(self, database_ref: str) -> dict[str, Any]: ...

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]: ...


class SimulatedAgent:
    """Adaptador: nunca toca Docker real. Marca `simulated: True`."""

    mode = "simulated"

    def deploy_installation(
        self, installation_id: str, eva_version: str, domain: str | None
    ) -> dict[str, Any]:
        return {
            "simulated": True,
            "installation_id": installation_id,
            "eva_version": eva_version,
            "domain": domain,
        }

    def upgrade_installation(self, installation_id: str, target_version: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "target_version": target_version}

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return {
            "simulated": True,
            "installation_id": installation_id,
            "service_name": service_name,
        }

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "status": "unknown"}

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]:
        # Sin cambios reales: no se inventan líneas de log.
        return {"simulated": True, "installation_id": installation_id, "lines": [], "limit": limit}

    def get_metrics(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "samples": []}

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref, "location_ref": None}

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref, "backup_ref": backup_ref}


def get_agent() -> OperationsAgent:
    return SimulatedAgent()
