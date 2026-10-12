"""Cliente del agente de operaciones (interfaz tipada, ADR-007).

- `SimulatedAgent`: no realiza cambios reales (por defecto).
- `HttpAgent`: llama al servicio del agente (modo `real`).
"""

from typing import Any, Protocol

from app.core.config import get_settings


class OperationsAgent(Protocol):
    mode: str

    def deploy_installation(self, spec: dict[str, Any]) -> dict[str, Any]: ...

    def upgrade_installation(self, spec: dict[str, Any]) -> dict[str, Any]: ...

    def remove_installation(self, installation_id: str) -> dict[str, Any]: ...

    def health_check(self, installation_id: str) -> dict[str, Any]: ...

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]: ...

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]: ...

    def get_metrics(self, installation_id: str) -> dict[str, Any]: ...

    def get_host_stats(self) -> dict[str, Any]: ...

    def request_backup(self, database_ref: str) -> dict[str, Any]: ...

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]: ...


class SimulatedAgent:
    mode = "simulated"

    def deploy_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        return {"simulated": True, "name": spec.get("name"), "image": spec.get("image")}

    def upgrade_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        return {"simulated": True, "name": spec.get("name"), "image": spec.get("image")}

    def remove_installation(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id}

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "services": []}

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "service_name": service_name}

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]:
        return {"simulated": True, "lines": [], "limit": limit}

    def get_metrics(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "samples": []}

    def get_host_stats(self) -> dict[str, Any]:
        return _empty_stats(simulated=True)

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref}

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref, "backup_ref": backup_ref}


class HttpAgent:
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
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def deploy_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        return self._call("deploy_installation", str(spec.get("installation_id", "")), spec)

    def upgrade_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        return self._call("upgrade_installation", str(spec.get("installation_id", "")), spec)

    def remove_installation(self, installation_id: str) -> dict[str, Any]:
        return self._call("remove_installation", installation_id, {})

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return self._call("health_check", installation_id, {})

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return self._call("restart_service", installation_id, {"service_name": service_name})

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]:
        return self._call("get_logs", installation_id, {"limit": limit})

    def get_metrics(self, installation_id: str) -> dict[str, Any]:
        return self._call("get_metrics", installation_id, {})

    def get_host_stats(self) -> dict[str, Any]:
        import httpx

        response = httpx.get(
            f"{self._base_url}/v1/host/stats",
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return self._call("request_backup", "", {"database_ref": database_ref})

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return self._call("request_restore", "", {"database_ref": database_ref, "backup_ref": backup_ref})


def _empty_stats(*, simulated: bool) -> dict[str, Any]:
    return {
        "simulated": simulated,
        "cpu_percent": 0.0,
        "cpu_count": 0,
        "mem_total": 0.0,
        "mem_used": 0.0,
        "mem_percent": 0.0,
        "disk_total": 0.0,
        "disk_used": 0.0,
        "disk_percent": 0.0,
        "load1": 0.0,
        "load5": 0.0,
        "load15": 0.0,
        "uptime_seconds": 0.0,
        "net_rx_bytes": 0.0,
        "net_tx_bytes": 0.0,
        "net_rx_rate": 0.0,
        "net_tx_rate": 0.0,
    }


def get_agent() -> OperationsAgent:
    settings = get_settings()
    if settings.agent_mode == "real" and settings.agent_url:
        return HttpAgent(settings.agent_url, settings.agent_token)
    return SimulatedAgent()
