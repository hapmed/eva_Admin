"""Interfaz y adaptador simulado del agente de operaciones."""

from typing import Any, Protocol


class OperationsAgent(Protocol):
    """Operaciones tipadas del agente. Sin parámetros arbitrarios."""

    mode: str

    def health_check(self, installation_id: str) -> dict[str, Any]: ...

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]: ...

    def upgrade_installation(
        self, installation_id: str, target_version: str
    ) -> dict[str, Any]: ...


class SimulatedAgent:
    """Adaptador de Fase 2: nunca toca Docker real."""

    mode = "simulated"

    def health_check(self, installation_id: str) -> dict[str, Any]:
        return {"simulated": True, "installation_id": installation_id, "status": "unknown"}

    def restart_service(self, installation_id: str, service_name: str) -> dict[str, Any]:
        return {
            "simulated": True,
            "accepted": True,
            "installation_id": installation_id,
            "service_name": service_name,
        }

    def upgrade_installation(
        self, installation_id: str, target_version: str
    ) -> dict[str, Any]:
        return {
            "simulated": True,
            "accepted": True,
            "installation_id": installation_id,
            "target_version": target_version,
        }


def get_agent() -> OperationsAgent:
    return SimulatedAgent()
