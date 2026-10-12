"""Modelos SQLAlchemy.

Importar este paquete registra todos los modelos en `Base.metadata` (lo usa
Alembic para autogenerar migraciones).
"""

from app.models.client import Client, ClientUser
from app.models.token import ApiToken
from app.models.user import HapmedUser, Permission, Role, role_permissions, user_roles

__all__ = [
    "ApiToken",
    "Client",
    "ClientUser",
    "HapmedUser",
    "Permission",
    "Role",
    "role_permissions",
    "user_roles",
]
