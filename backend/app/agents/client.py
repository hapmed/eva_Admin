"""Cliente del agente de operaciones (interfaz tipada, ADR-007).

- `SimulatedAgent`: no realiza cambios reales (por defecto).
- `HttpAgent`: llama al servicio del agente (modo `real`).
"""

from typing import Any, Protocol

from app.core.config import get_settings


class OperationsAgent(Protocol):
    mode: str

    def health_check(self, installation_id: str) -> dict[str, Any]: ...

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]: ...

    def upgrade_installation(self, installation_id: str, target_version: str) -> dict[str, Any]: ...

    def deploy_installation(
        self, installation_id: str, eva_version: str, domain: str | None
    ) -> dict[str, Any]: ...

    def request_backup(self, database_ref: str) -> dict[str, Any]: ...

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]: ...

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]: ...

    def get_metrics(self, installation_id: str) -> dict[str, Any]: ...


class SimulatedAgent:
    mode = "simulated"

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "status": "unknown"}

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "service_name": service_name}

    def upgrade_installation(self, installation_id: str, target_version: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "target_version": target_version}

    def deploy_installation(
        self, installation_id: str, eva_version: str, domain: str | None
    ) -> dict[str, Any]:
        return {
            "simulated": True,
            "installation_id": installation_id,
            "eva_version": eva_version,
            "domain": domain,
        }

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref}

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref, "backup_ref": backup_ref}

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]:
        return {"simulated": True, "lines": [], "limit": limit}

    def get_metrics(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "samples": []}


class HttpAgent:
    """Llama al servicio del agente por HTTP (modo real)."""

    mode = "real"

    def __init__(self, base_url: str, token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token

    def _call(self, operation_type: str, installation_id: str, params: dict[str, Any]) -> dict[str, Any]:
        import httpx

        response = httpx.post(
            f"{self._base_url}/v1/operations",
            json={"type": operation_type, "installation_id": installation_id, "params": params},
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return self._call("health_check", installation_id, {})

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return self._call("restart_service", installation_id, {"service_name": service_name})

    def upgrade_installation(self, installation_id: str, target_version: str) -> dict[str, Any]:
        return self._call("upgrade_installation", installation_id, {"target_version": target_version})

    def deploy_installation(
        self, installation_id: str, eva_version: str, domain: str | None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"eva_version": eva_version}
        if domain:
            params["domain"] = domain
        return self._call("deploy_installation", installation_id, params)

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return self._call("request_backup", "", {"database_ref": database_ref})

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return self._call("request_restore", "", {"database_ref": database_ref, "backup_ref": backup_ref})

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]:
        # El servicio del agente aún no expone logs por HTTP; se devuelve vacío.
        return {"simulated": False, "lines": [], "limit": limit}

    def get_metrics(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": False, "samples": []}


def get_agent() -> OperationsAgent:
    settings = get_settings()
    if settings.agent_mode == "real" and settings.agent_url:
        return HttpAgent(settings.agent_url, settings.agent_token)
    return SimulatedAgent()
