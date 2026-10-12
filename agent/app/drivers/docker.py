"""Driver real de Docker (SDK de Docker).

Solo opera sobre recursos **gestionados** por EVAS Admin (label
`evas.managed_by=evas-admin`) y con operaciones tipadas. Las operaciones que
requieren el manifiesto de despliegue (deploy/upgrade) o respaldo quedan
explícitamente **no soportadas** hasta implementar ese flujo.
"""

from datetime import UTC, datetime
from typing import Any

import docker
from docker.errors import DockerException, NotFound

_SENSITIVE = ("password", "secret", "token", "authorization", "cookie", "connection string")


class RealDockerDriver:
    mode = "real"

    def __init__(self) -> None:
        from app.config import get_settings

        self._settings = get_settings()
        self._client = docker.DockerClient(base_url=self._settings.docker_host, timeout=30)

    def _filters(self, installation_id: str) -> dict[str, list[str]]:
        return {
            "label": [
                f"{self._settings.managed_label}=evas-admin",
                f"evas.installation_id={installation_id}",
            ]
        }

    def _find(self, installation_id: str, service_name: str | None = None):
        containers = self._client.containers.list(all=True, filters=self._filters(installation_id))
        if not containers:
            raise NotFound(f"instalación {installation_id} no encontrada")
        if service_name:
            for container in containers:
                if (
                    container.name == service_name
                    or container.labels.get("evas.service") == service_name
                ):
                    return container
            raise NotFound(f"servicio {service_name} no encontrado")
        return containers[0]

    @staticmethod
    def _sanitize(line: str) -> str:
        lowered = line.lower()
        for needle in _SENSITIVE:
            if needle in lowered:
                return "[redactado]"
        return line

    def health_check(self, installation_id: str) -> dict[str, Any]:
        containers = self._client.containers.list(all=True, filters=self._filters(installation_id))
        services = []
        for container in containers:
            state = container.attrs.get("State", {})
            services.append(
                {
                    "name": container.name,
                    "status": state.get("Status"),
                    "health": (state.get("Health") or {}).get("Status", "none"),
                }
            )
        return {"simulated": False, "installation_id": installation_id, "services": services}

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        container = self._find(installation_id, service_name)
        container.restart(timeout=30)
        return {
            "simulated": False,
            "installation_id": installation_id,
            "service_name": service_name,
            "restarted": True,
        }

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]:
        try:
            container = self._find(installation_id)
            raw = container.logs(tail=limit).decode("utf-8", errors="replace")
            lines = [self._sanitize(line) for line in raw.splitlines()][-limit:]
        except (NotFound, DockerException):
            lines = []
        return {
            "simulated": False,
            "installation_id": installation_id,
            "lines": lines,
            "limit": limit,
        }

    def get_metrics(self, installation_id: str) -> dict[str, Any]:
        try:
            stats = self._find(installation_id).stats(stream=False)
        except (NotFound, DockerException):
            return {"simulated": False, "installation_id": installation_id, "samples": []}

        cpu = 0.0
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
            )
            cores = (
                stats["cpu_stats"].get("online_cpus")
                or len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", []))
                or 1
            )
            if system_delta > 0:
                cpu = round((cpu_delta / system_delta) * cores * 100, 2)
        except (KeyError, TypeError, ZeroDivisionError):
            cpu = 0.0

        ram = 0.0
        try:
            limit = stats["memory_stats"]["limit"]
            ram = round(stats["memory_stats"]["usage"] / limit * 100, 2) if limit else 0.0
        except (KeyError, TypeError, ZeroDivisionError):
            ram = 0.0

        now = datetime.now(UTC).isoformat()
        return {
            "simulated": False,
            "installation_id": installation_id,
            "samples": [
                {"metric_type": "cpu", "value": cpu, "captured_at": now},
                {"metric_type": "ram", "value": ram, "captured_at": now},
            ],
        }

    # --- Operaciones que requieren el manifiesto de despliegue ---
    def deploy_installation(
        self, installation_id: str, eva_version: str, domain: str | None
    ) -> dict[str, Any]:
        raise RuntimeError("deploy real no habilitado: requiere el manifiesto de despliegue")

    def upgrade_installation(self, installation_id: str, target_version: str) -> dict[str, Any]:
        raise RuntimeError("upgrade real no habilitado: requiere el manifiesto de despliegue")

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        raise RuntimeError("backup real no habilitado: usa el timer de respaldos del host")

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        raise RuntimeError("restore real no habilitado: usa el flujo autorizado del host")
