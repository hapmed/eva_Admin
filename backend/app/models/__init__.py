"""Modelos SQLAlchemy.

Importar este paquete registra todos los modelos en `Base.metadata` (lo usa
Alembic para autogenerar migraciones).
"""

from app.models.audit import AuditLog
from app.models.client import Client, ClientUser
from app.models.eva import EvaProduct, EvaVersion
from app.models.infrastructure import (
    DatabaseRecord,
    Domain,
    Installation,
    InstallationConfig,
    InstallationService,
    Node,
    Operation,
    SecretReference,
)
from app.models.monitoring import AlertState, Backup, HealthCheck, Metric
from app.models.subscription import Plan, Subscription, SubscriptionEvent
from app.models.token import ApiToken
from app.models.user import HapmedUser, Permission, Role, role_permissions, user_roles

__all__ = [
    "AlertState",
    "ApiToken",
    "AuditLog",
    "Backup",
    "Client",
    "ClientUser",
    "DatabaseRecord",
    "Domain",
    "EvaProduct",
    "EvaVersion",
    "HapmedUser",
    "HealthCheck",
    "Installation",
    "InstallationConfig",
    "InstallationService",
    "Metric",
    "Node",
    "Operation",
    "Permission",
    "Plan",
    "Role",
    "SecretReference",
    "Subscription",
    "SubscriptionEvent",
    "role_permissions",
    "user_roles",
]
