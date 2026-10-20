"""Lógica de planes y suscripciones.

Estados y transiciones válidas. Fechas en UTC. Sin procesamiento de pagos.
No se suspenden ni borran instalaciones automáticamente (ver docs).
"""

import calendar
import math
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.models.eva import EvaProduct
from app.models.subscription import Plan, Subscription, SubscriptionEvent
from app.schemas.subscription import PlanCreate, SubscriptionCreate
from app.services import audit
from app.services.util import as_uuid

# Los planes nuevos solo admiten monthly/yearly (ver PlanCreate).
# "quarterly" se conserva para poder renovar planes históricos ya existentes.
PERIOD_MONTHS: dict[str, int] = {"monthly": 1, "quarterly": 3, "yearly": 12}
EXPIRING_DAYS = 14
CANCELLED = "cancelled"


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def create_plan(db: Session, context: AuthContext, data: PlanCreate) -> Plan:
    if db.scalar(select(Plan).where(Plan.code == data.code)):
        raise ValueError("el código de plan ya existe")
    plan = Plan(
        code=data.code,
        name=data.name,
        billing_period=data.billing_period,
        price=data.price,
        currency=data.currency,
    )
    db.add(plan)
    db.flush()
    audit.record(db, context, "plan.create", "plan", plan.id, code=plan.code)
    db.commit()
    db.refresh(plan)
    return plan


def list_plans(db: Session) -> list[Plan]:
    return list(db.scalars(select(Plan).order_by(Plan.code)).all())


def _period_months(db: Session, plan_id) -> int:
    plan = db.get(Plan, plan_id)
    if plan is None:
        raise LookupError("plan no encontrado")
    return PERIOD_MONTHS[plan.billing_period]


def create_subscription(db: Session, context: AuthContext, data: SubscriptionCreate) -> Subscription:
    from app.services import client_service

    client = client_service.get_client(db, data.client_id)
    plan = db.get(Plan, as_uuid(data.plan_id))
    if plan is None:
        raise LookupError("plan no encontrado")
    if not plan.is_active:
        raise ValueError("el plan no está activo")
    eva_product_id = None
    if data.eva_product_id:
        eva = db.get(EvaProduct, as_uuid(data.eva_product_id))
        if eva is None:
            raise LookupError("EVA no encontrada")
        eva_product_id = eva.id

    start = datetime.now(UTC)
    end = add_months(start, PERIOD_MONTHS[plan.billing_period])
    subscription = Subscription(
        client_id=client.id,
        plan_id=plan.id,
        eva_product_id=eva_product_id,
        status="active",
        start_date=start,
        renewal_date=end,
        end_date=end,
        auto_renew=data.auto_renew,
    )
    db.add(subscription)
    db.flush()
    db.add(
        SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="created",
            from_status=None,
            to_status="active",
            actor_id=context.actor_id,
        )
    )
    audit.record(
        db, context, "subscription.create", "subscription", subscription.id, client_id=str(client.id)
    )
    db.commit()
    db.refresh(subscription)
    return subscription


def list_subscriptions(
    db: Session, client_id: str | None = None, status: str | None = None
) -> list[Subscription]:
    stmt = select(Subscription).order_by(Subscription.created_at)
    if client_id:
        stmt = stmt.where(Subscription.client_id == as_uuid(client_id))
    if status:
        stmt = stmt.where(Subscription.status == status)
    return list(db.scalars(stmt).all())


def get_subscription(db: Session, subscription_id: str) -> Subscription:
    subscription = db.get(Subscription, as_uuid(subscription_id))
    if subscription is None:
        raise LookupError("suscripción no encontrada")
    return subscription


def list_events(db: Session, subscription_id: str) -> list[SubscriptionEvent]:
    subscription = get_subscription(db, subscription_id)
    return list(
        db.scalars(
            select(SubscriptionEvent)
            .where(SubscriptionEvent.subscription_id == subscription.id)
            .order_by(SubscriptionEvent.occurred_at)
        ).all()
    )


def renew(db: Session, context: AuthContext, subscription_id: str, notes: str = "") -> Subscription:
    subscription = get_subscription(db, subscription_id)
    if subscription.status == CANCELLED:
        raise ValueError("no se puede renovar una suscripción cancelada")
    months = _period_months(db, subscription.plan_id)
    base = max(_aware(subscription.end_date), datetime.now(UTC))
    new_end = add_months(base, months)
    from_status = subscription.status
    subscription.end_date = new_end
    subscription.renewal_date = new_end
    subscription.status = "active"
    db.add(
        SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="renewed",
            from_status=from_status,
            to_status="active",
            actor_id=context.actor_id,
            notes=notes,
        )
    )
    audit.record(db, context, "subscription.renew", "subscription", subscription.id)
    db.commit()
    db.refresh(subscription)
    return subscription


def cancel(db: Session, context: AuthContext, subscription_id: str, notes: str = "") -> Subscription:
    subscription = get_subscription(db, subscription_id)
    if subscription.status == CANCELLED:
        raise ValueError("la suscripción ya está cancelada")
    from_status = subscription.status
    subscription.status = CANCELLED
    db.add(
        SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="cancelled",
            from_status=from_status,
            to_status=CANCELLED,
            actor_id=context.actor_id,
            notes=notes,
        )
    )
    audit.record(db, context, "subscription.cancel", "subscription", subscription.id)
    db.commit()
    db.refresh(subscription)
    return subscription


@dataclass(frozen=True)
class SubscriptionTiming:
    """Tiempo de la suscripción: total, transcurrido, restante y vencido."""

    days_total: int
    days_elapsed: int
    days_remaining: int
    days_overdue: int
    progress_percent: float
    is_expired: bool


def subscription_timing(subscription: Subscription) -> SubscriptionTiming:
    now = datetime.now(UTC)
    start = _aware(subscription.start_date)
    end = _aware(subscription.end_date)
    total_seconds = max((end - start).total_seconds(), 1.0)
    elapsed_seconds = (now - start).total_seconds()

    days_total = max(1, math.ceil(total_seconds / 86400))
    days_elapsed = min(days_total, max(0, int(elapsed_seconds // 86400)))
    days_remaining = max(0, math.ceil((end - now).total_seconds() / 86400))
    days_overdue = max(0, int((now - end).total_seconds() // 86400))
    progress_percent = round(min(max(elapsed_seconds / total_seconds * 100, 0.0), 100.0), 1)

    return SubscriptionTiming(
        days_total=days_total,
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        days_overdue=days_overdue,
        progress_percent=progress_percent,
        is_expired=now >= end,
    )


def days_to_expiry(subscription: Subscription) -> int:
    return subscription_timing(subscription).days_remaining


def is_expiring_soon(subscription: Subscription) -> bool:
    if subscription.status not in {"active", "grace"}:
        return False
    return days_to_expiry(subscription) <= EXPIRING_DAYS
