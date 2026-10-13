"""Driver real de Docker (SDK de Docker).

Solo opera sobre recursos **gestionados** por EVAS Admin (label
`evas.managed_by=evas-admin`). Deploy/upgrade crean el contenedor de la EVA con
un *spec* tipado; backup/restore quedan explícitamente no soportados.
"""

import io
import os
import tarfile
import time
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
        migrate = str(spec.get("migrate") or "").strip()

        self._client.images.pull(image)
        self._remove_by_name(name)

        if migrate:
            self._run_migrate(image, migrate, environment, network, labels)

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
            "migrated": bool(migrate),
        }

    def _run_migrate(
        self,
        image: str,
        migrate: str,
        environment: dict[str, Any],
        network: str,
        labels: dict[str, Any],
    ) -> None:
        """Ejecuta el comando de migración en un contenedor efímero (idempotente)."""
        try:
            self._client.containers.run(
                image=image,
                command=["sh", "-lc", migrate],
                environment=environment,
                network=network,
                labels=labels,
                remove=True,
            )
        except DockerException as exc:
            raise RuntimeError("fallo la migración de la EVA") from exc

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

    # --- Respaldos (pg_dump/pg_restore vía el contenedor PostgreSQL) ---
    def _postgres(self):
        return self._client.containers.get(self._settings.postgres_container)

    def _postgres_user(self) -> str:
        for entry in self._postgres().attrs["Config"].get("Env", []):
            if entry.startswith("POSTGRES_USER="):
                return entry.split("=", 1)[1]
        return "postgres"

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        container = self._postgres()
        user = self._postgres_user()
        target_dir = os.path.join(self._settings.backup_dir, database_ref)
        os.makedirs(target_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        filename = f"{database_ref}_{timestamp}.dump"
        path = os.path.join(target_dir, filename)

        result = container.exec_run(["sh", "-c", f'pg_dump -U "{user}" -Fc "{database_ref}"'])
        if result.exit_code != 0:
            raise RuntimeError("fallo pg_dump")
        with open(path, "wb") as handle:
            handle.write(result.output)
        return {
            "simulated": False,
            "database_ref": database_ref,
            "location_ref": f"{database_ref}/{filename}",
            "size_bytes": len(result.output),
        }

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        container = self._postgres()
        user = self._postgres_user()
        source = os.path.join(self._settings.backup_dir, backup_ref)
        if not os.path.exists(source):
            raise RuntimeError("copia de seguridad no encontrada")

        # Snapshot previo de seguridad.
        self.request_backup(database_ref)

        with open(source, "rb") as handle:
            data = handle.read()
        name = os.path.basename(backup_ref)
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as tar:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        buffer.seek(0)
        container.put_archive("/tmp", buffer)

        container.exec_run(
            [
                "psql",
                "-U",
                user,
                "-d",
                "postgres",
                "-c",
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname='{database_ref}' AND pid <> pg_backend_pid()",
            ]
        )
        result = container.exec_run(
            [
                "pg_restore",
                "-U",
                user,
                "--clean",
                "--if-exists",
                "--no-owner",
                "--dbname",
                database_ref,
                f"/tmp/{name}",
            ]
        )
        if result.exit_code not in (0, 1):
            raise RuntimeError("fallo pg_restore")
        return {
            "simulated": False,
            "database_ref": database_ref,
            "backup_ref": backup_ref,
            "restored": True,
        }
