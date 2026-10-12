"""Monitoreo: healthchecks, logs saneados y métricas (vía agente)."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.client import get_agent
from app.models.infrastructure import Installation
from app.models.monitoring import HealthCheck


def record_health_check(db: Session, installation: Installation) -> None:
    now = datetime.now(UTC)
    for service in installation.services:
        db.add(HealthCheck(installation_service_id=service.id, status="unknown", checked_at=now))
        service.health_status = "unknown"
        service.last_checked_at = now


def service_health(db: Session, installation: Installation) -> list[dict]:
    result = []
    for service in installation.services:
        check = db.scalar(
            select(HealthCheck)
            .where(HealthCheck.installation_service_id == service.id)
            .order_by(HealthCheck.checked_at.desc())
        )
        result.append(
            {
                "service_name": service.service_name,
                "status": service.status,
                "health_status": service.health_status,
                "last_checked_at": check.checked_at if check else service.last_checked_at,
            }
        )
    return result


def get_logs(installation: Installation, limit: int = 200) -> dict:
    result = get_agent().get_logs(str(installation.id), limit)
    lines = list(result.get("lines", []))[:limit]
    return {
        "simulated": bool(result.get("simulated", True)),
        "lines": lines,
        "retention_note": "tamaño y retención limitados; sin secretos",
    }


def get_metrics(installation: Installation) -> dict:
    result = get_agent().get_metrics(str(installation.id))
    return {"simulated": bool(result.get("simulated", True)), "samples": result.get("samples", [])}
