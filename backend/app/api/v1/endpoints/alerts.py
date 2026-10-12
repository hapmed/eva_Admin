"""Alertas (cálculo y gestión de estado)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.db.session import get_db
from app.schemas.monitoring import AlertAction, AlertOut
from app.services import alerts_service

router = APIRouter()


@router.get("", response_model=list[AlertOut])
def list_alerts(
    _: AuthContext = Depends(require_permission("alerts:read")), db: Session = Depends(get_db)
) -> list[dict]:
    return alerts_service.compute_alerts(db)


@router.post("/acknowledge", response_model=AlertOut)
def acknowledge_alert(
    data: AlertAction,
    _: AuthContext = Depends(require_permission("alerts:write")),
    db: Session = Depends(get_db),
) -> dict:
    alerts_service.set_state(db, data.key, "acknowledged")
    return next(
        (alert for alert in alerts_service.compute_alerts(db) if alert["key"] == data.key),
        {
            "key": data.key,
            "type": "unknown",
            "severity": "info",
            "entity_type": "unknown",
            "entity_id": "",
            "message": "",
            "status": "acknowledged",
        },
    )


@router.post("/resolve", response_model=AlertOut)
def resolve_alert(
    data: AlertAction,
    _: AuthContext = Depends(require_permission("alerts:write")),
    db: Session = Depends(get_db),
) -> dict:
    alerts_service.set_state(db, data.key, "resolved")
    return next(
        (alert for alert in alerts_service.compute_alerts(db) if alert["key"] == data.key),
        {
            "key": data.key,
            "type": "unknown",
            "severity": "info",
            "entity_type": "unknown",
            "entity_id": "",
            "message": "",
            "status": "resolved",
        },
    )
