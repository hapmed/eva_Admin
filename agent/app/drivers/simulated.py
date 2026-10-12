"""Driver simulado: nunca realiza cambios reales (por defecto)."""

from typing import Any


class SimulatedDriver:
    mode = "simulated"

    def deploy_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        return {"simulated": True, "name": spec.get("name"), "image": spec.get("image")}

    def upgrade_installation(self, spec: dict[str, Any]) -> dict[str, Any]:
        return {"simulated": True, "name": spec.get("name"), "image": spec.get("image")}

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "service_name": service_name}

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "services": []}

    def get_logs(self, installation_id: str, limit: int = 200) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "lines": [], "limit": limit}

    def get_metrics(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "samples": []}

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref}

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref, "backup_ref": backup_ref}
