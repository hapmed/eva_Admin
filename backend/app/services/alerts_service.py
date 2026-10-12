"""Alertas: cálculo a partir del estado del dominio y gestión ack/resolve."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.infrastructure import DatabaseRecord, Installation
from app.models.monitoring import AlertState
from app.models.subscription import Subscription
from app.services import subscription_service


def _state_map(db: Session) -> dict[str, str]:
    return {state.key: state.status for state in db.scalars(select(AlertState)).all()}


def compute_alerts(db: Session) -> list[dict]:
    states = _state_map(db)
    alerts: list[dict] = []

    def add(key: str, type_: str, severity: str, entity_type: str, entity_id, message: str) -> None:
        alerts.append(
            {
                "key": key,
                "type": type_,
                "severity": severity,
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "message": message,
                "status": states.get(key, "open"),
            }
        )

    for subscription in db.scalars(select(Subscription)).all():
        if subscription.status not in {"active", "grace"}:
            continue
        days = subscription_service.days_to_expiry(subscription)
        if days <= 0:
            add(
                f"subscription:{subscription.id}:expired",
                "subscription_expired",
                "critical",
                "subscription",
                subscription.id,
                "Suscripción vencida",
            )
        elif subscription_service.is_expiring_soon(subscription):
            add(
                f"subscription:{subscription.id}:expiring",
                "subscription_expiring",
                "warning",
                "subscription",
                subscription.id,
                f"Vence en {days} días",
            )

    for installation in db.scalars(select(Installation)).all():
        if installation.status in {"degraded", "failed"}:
            add(
                f"installation:{installation.id}:health",
                "health_degraded",
                "critical",
                "installation",
                installation.id,
                "Instalación degradada o fallida",
            )

    for record in db.scalars(select(DatabaseRecord)).all():
        if record.last_backup_at is None:
            add(
                f"database:{record.id}:backup",
                "backup_missing",
                "warning",
                "database_record",
                record.id,
                "Sin copia de seguridad registrada",
            )

    return alerts


def set_state(db: Session, key: str, status: str) -> AlertState:
    state = db.scalar(select(AlertState).where(AlertState.key == key))
    if state is None:
        state = AlertState(key=key, status=status)
        db.add(state)
    else:
        state.status = status
    db.commit()
    db.refresh(state)
    return state
