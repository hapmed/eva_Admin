"""Serializadores ORM → dict (coinciden con los esquemas de respuesta)."""

from app.models.client import Client, ClientUser
from app.models.eva import EvaProduct, EvaVersion
from app.models.subscription import Plan, Subscription, SubscriptionEvent
from app.models.user import HapmedUser, Permission, Role


def user_out(user: HapmedUser) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "mfa_enabled": user.mfa_enabled,
        "roles": sorted(role.code for role in user.roles),
        "created_at": user.created_at,
    }


def permission_out(permission: Permission) -> dict:
    return {"code": permission.code, "description": permission.description}


def role_out(role: Role) -> dict:
    return {
        "id": str(role.id),
        "code": role.code,
        "name": role.name,
        "is_system": role.is_system,
        "permissions": sorted(p.code for p in role.permissions),
    }


def client_out(client: Client) -> dict:
    return {
        "id": str(client.id),
        "legal_name": client.legal_name,
        "display_name": client.display_name,
        "tax_id": client.tax_id,
        "status": client.status,
        "notes": client.notes,
        "created_at": client.created_at,
    }


def client_user_out(user: ClientUser) -> dict:
    return {
        "id": str(user.id),
        "client_id": str(user.client_id),
        "email": user.email,
        "role_code": user.role_code,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


def eva_version_out(version: EvaVersion) -> dict:
    return {
        "id": str(version.id),
        "version": version.version,
        "status": version.status,
        "deployment_requirements": version.deployment_requirements or {},
        "created_at": version.created_at,
    }


def eva_out(eva: EvaProduct) -> dict:
    return {
        "id": str(eva.id),
        "code": eva.code,
        "name": eva.name,
        "description": eva.description,
        "status": eva.status,
        "versions": [
            eva_version_out(version) for version in sorted(eva.versions, key=lambda item: item.created_at)
        ],
        "created_at": eva.created_at,
    }


def plan_out(plan: Plan) -> dict:
    return {
        "id": str(plan.id),
        "code": plan.code,
        "name": plan.name,
        "billing_period": plan.billing_period,
        "price": plan.price,
        "currency": plan.currency,
        "is_active": plan.is_active,
    }


def subscription_out(subscription: Subscription, days_to_expiry: int, expiring_soon: bool) -> dict:
    return {
        "id": str(subscription.id),
        "client_id": str(subscription.client_id),
        "plan_id": str(subscription.plan_id),
        "eva_product_id": str(subscription.eva_product_id) if subscription.eva_product_id else None,
        "status": subscription.status,
        "start_date": subscription.start_date,
        "renewal_date": subscription.renewal_date,
        "end_date": subscription.end_date,
        "auto_renew": subscription.auto_renew,
        "days_to_expiry": days_to_expiry,
        "expiring_soon": expiring_soon,
    }


def subscription_event_out(event: SubscriptionEvent) -> dict:
    return {
        "id": str(event.id),
        "event_type": event.event_type,
        "from_status": event.from_status,
        "to_status": event.to_status,
        "notes": event.notes,
        "occurred_at": event.occurred_at,
    }
