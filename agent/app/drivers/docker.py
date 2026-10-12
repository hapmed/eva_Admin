"""Driver real de Docker.

Fase 2 NO habilita operaciones reales. Este driver existe para dejar el contrato
listo, pero rechaza cualquier acción hasta que se autorice el modo `real` y se
revise la seguridad. No se importa ni se construye salvo en modo `real`.
"""

from typing import Any


class RealDockerDriver:
    mode = "real"

    def __init__(self) -> None:
        from app.config import get_settings

        self._settings = get_settings()

    def _refuse(self) -> dict[str, Any]:
        raise RuntimeError(
            "Modo real no habilitado en Fase 2. Requiere autorización y revisión "
            "de seguridad (ver docs/EVAS_ADMIN/SECURITY.md)."
        )

    def deploy_installation(
        self, installation_id: str, eva_version: str, domain: str | None
    ) -> dict[str, Any]:
        return self._refuse()

    def upgrade_installation(
        self, installation_id: str, target_version: str
    ) -> dict[str, Any]:
        return self._refuse()

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return self._refuse()

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return self._refuse()

    def request_backup(self, database_ref: str) -> dict[str, Any]:
        return self._refuse()

    def request_restore(self, database_ref: str, backup_ref: str) -> dict[str, Any]:
        return self._refuse()
