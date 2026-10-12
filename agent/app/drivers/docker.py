"""Driver real de Docker (SDK de Docker).

Solo opera sobre recursos **gestionados** por EVAS Admin (label
`evas.managed_by=evas-admin`). Deploy/upgrade crean el contenedor de la EVA con
un *spec* tipado; backup/restore quedan explícitamente no soportados.
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
        self._client = docker.DockerClient(base_url=self._settings.docker_host, timeout=60)

    # --- Deploy / upgrade / remove ---

    def _remove_by_name(self, name: str) -> None:
        try:
            container = self._client.containers.get(name)
            container.remove(force=True)
        except NotFound:
            pass

    def deploy_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        name = str(spec["name"])
        image = str(spec["image"])
        network = str(spec.get("network") or self._settings.eva_network)
        host_port = int(spec["host_port"])
        container_port = int(spec.get("container_port", 8000))
        environment = spec.get("env") or {}
        labels = spec.get("labels") or {}

        self._client.images.pull(image)
        self._remove_by_name(name)

        container = self._client.containers.create(
            image=image,
            name=name,
            detach=True,
            environment=environment,
            labels=labels,
            ports={f"{container_port}/tcp": ("127.0.0.1", host_port)},
            network=network,
            restart_policy={"Name": "unless-stopped"},
        )
        container.start()
        return {
            "simulated": False,
            "name": name,
            "image": image,
            "container_id": container.id,
            "host_port": host_port,
        }

    def upgrade_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        return self.deploy_installation(spec)

    def remove_installation(self, installation_id: str) -> dict[str, Any]:
        containers = self._client.containers.list(all=True, filters=self._filters(installation_id))
        removed = []
        for container in containers:
            container.remove(force=True)
            removed.append(container.name)
        return {"simulated": False, "installation_id": installation_id, "removed": removed}

    # --- Consultas ---

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

    # --- Respaldos (pendiente: flujo autorizado del host) ---
    def request_backup(self, database_ref: str) -> dict[str, Any]:
        raise RuntimeError("backup real no habilitado: usa el timer de respaldos del host")

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        raise RuntimeError("restore real no habilitado: usa el flujo autorizado del host")
