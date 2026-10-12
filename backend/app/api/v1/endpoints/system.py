"""Estado del servidor (métricas del host vía agente)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.client import get_agent
from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.schemas.system import SystemStats

router = APIRouter(tags=["system"])


@router.get("/system", response_model=SystemStats)
def system_stats(
    _: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)
) -> dict:
    try:
        return get_agent().get_host_stats()
    except Exception:  # noqa: BLE001 - no romper el dashboard si el agente falla
        return get_host_stats_fallback()


def get_host_stats_fallback() -> dict:
    return {
        "simulated": True,
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
