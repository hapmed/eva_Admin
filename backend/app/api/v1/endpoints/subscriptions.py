"""Suscripciones."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import subscription_event_out, subscription_out
from app.db.session import get_db
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionEventOut,
    SubscriptionOut,
    SubscriptionRenew,
)
from app.services import subscription_service

router = APIRouter()


def _out(subscription) -> dict:
    return subscription_out(
        subscription,
        subscription_service.subscription_timing(subscription),
        subscription_service.is_expiring_soon(subscription),
    )


@router.get("", response_model=list[SubscriptionOut])
def list_subscriptions(
    client_id: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    _: AuthContext = Depends(require_permission("subscriptions:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    subscriptions = subscription_service.list_subscriptions(db, client_id, status_filter)
    return [_out(subscription) for subscription in subscriptions]


@router.post("", response_model=SubscriptionOut, status_code=201)
def create_subscription(
    data: SubscriptionCreate,
    context: AuthContext = Depends(require_permission("subscriptions:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        subscription = subscription_service.create_subscription(db, context, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return _out(subscription)


@router.get("/{subscription_id}", response_model=SubscriptionOut)
def get_subscription(
    subscription_id: str,
    _: AuthContext = Depends(require_permission("subscriptions:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        subscription = subscription_service.get_subscription(db, subscription_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return _out(subscription)


@router.post("/{subscription_id}/renew", response_model=SubscriptionOut)
def renew_subscription(
    subscription_id: str,
    data: SubscriptionRenew,
    context: AuthContext = Depends(require_permission("subscriptions:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        subscription = subscription_service.renew(db, context, subscription_id, data.notes)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return _out(subscription)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionOut)
def cancel_subscription(
    subscription_id: str,
    data: SubscriptionRenew,
    context: AuthContext = Depends(require_permission("subscriptions:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        subscription = subscription_service.cancel(db, context, subscription_id, data.notes)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return _out(subscription)


@router.get("/{subscription_id}/events", response_model=list[SubscriptionEventOut])
def list_events(
    subscription_id: str,
    _: AuthContext = Depends(require_permission("subscriptions:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    try:
        events = subscription_service.list_events(db, subscription_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return [subscription_event_out(event) for event in events]
