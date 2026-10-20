"""Esquemas de planes y suscripciones."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PlanCreate(BaseModel):
    code: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=120)
    billing_period: str = Field(pattern="^(monthly|yearly)$")
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class PlanOut(BaseModel):
    id: str
    code: str
    name: str
    billing_period: str
    price: Decimal
    currency: str
    is_active: bool


class SubscriptionCreate(BaseModel):
    client_id: str
    plan_id: str
    eva_product_id: str | None = None
    auto_renew: bool = False


class SubscriptionOut(BaseModel):
    id: str
    client_id: str
    plan_id: str
    eva_product_id: str | None
    status: str
    start_date: datetime
    renewal_date: datetime
    end_date: datetime
    auto_renew: bool
    days_to_expiry: int
    days_total: int
    days_elapsed: int
    days_overdue: int
    progress_percent: float
    is_expired: bool
    expiring_soon: bool


class SubscriptionEventOut(BaseModel):
    id: str
    event_type: str
    from_status: str | None
    to_status: str | None
    notes: str
    occurred_at: datetime


class SubscriptionRenew(BaseModel):
    notes: str = Field(default="", max_length=300)
