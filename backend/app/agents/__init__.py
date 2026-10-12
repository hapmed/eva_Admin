"""Cliente del agente de operaciones.

Interfaz tipada hacia el agente (ADR-007). En Fase 2 sólo existe el adaptador
`SimulatedAgent`, que NO realiza cambios reales.
"""

from app.agents.client import OperationsAgent, SimulatedAgent, get_agent

__all__ = ["OperationsAgent", "SimulatedAgent", "get_agent"]
