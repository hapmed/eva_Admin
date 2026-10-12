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
        "config_schema": eva.config_schema or {},
        "image_repo": eva.image_repo or "",
        "container_port": eva.container_port,
        "healthcheck_path": eva.healthcheck_path or "/healthz",
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


def node_out(node) -> dict:
    return {
        "id": str(node.id),
        "name": node.name,
        "host_ref": node.host_ref,
        "environment": node.environment,
        "status": node.status,
    }


def service_out(service) -> dict:
    return {
        "id": str(service.id),
        "service_name": service.service_name,
        "container_ref": service.container_ref,
        "image_ref": service.image_ref,
        "status": service.status,
        "health_status": service.health_status,
        "last_checked_at": service.last_checked_at,
    }


def secret_ref_out(reference) -> dict:
    return {"key": reference.key, "provider": reference.provider}


def installation_out(installation, secrets: list) -> dict:
    return {
        "id": str(installation.id),
        "client_id": str(installation.client_id),
        "eva_product_id": str(installation.eva_product_id),
        "subscription_id": str(installation.subscription_id) if installation.subscription_id else None,
        "node_id": str(installation.node_id) if installation.node_id else None,
        "environment": installation.environment,
        "status": installation.status,
        "desired_version": installation.desired_version,
        "installed_version": installation.installed_version,
        "last_operation_at": installation.last_operation_at,
        "host_port": installation.host_port,
        "container_name": installation.container_name,
        "services": [service_out(service) for service in installation.services],
        "domains": [domain.fqdn for domain in installation.domains],
        "secrets": [secret_ref_out(reference) for reference in secrets],
    }


def domain_out(domain) -> dict:
    return {
        "id": str(domain.id),
        "installation_id": str(domain.installation_id),
        "fqdn": domain.fqdn,
        "kind": domain.kind,
        "status": domain.status,
    }


def database_out(record) -> dict:
    return {
        "id": str(record.id),
        "installation_id": str(record.installation_id),
        "engine": record.engine,
        "logical_name": record.logical_name,
        "host_ref": record.host_ref,
        "status": record.status,
        "last_backup_at": record.last_backup_at,
    }


def operation_out(operation) -> dict:
    return {
        "id": str(operation.id),
        "installation_id": str(operation.installation_id) if operation.installation_id else None,
        "type": operation.type,
        "status": operation.status,
        "requested_at": operation.requested_at,
        "finished_at": operation.finished_at,
        "result_summary": operation.result_summary,
        "error_code": operation.error_code,
        "simulated": operation.simulated,
    }
