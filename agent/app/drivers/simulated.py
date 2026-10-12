"""Driver simulado: nunca realiza cambios reales (Fase 2)."""

from typing import Any


class SimulatedDriver:
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
        return {
            "simulated": True,
            "installation_id": installation_id,
            "target_version": target_version,
        }

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return {
            "simulated": True,
            "installation_id": installation_id,
            "service_name": service_name,
        }

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "status": "unknown"}

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref, "location_ref": None}

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return {"simulated": True, "database_ref": database_ref, "backup_ref": backup_ref}
