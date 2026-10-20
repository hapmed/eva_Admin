"""Credenciales de administrador de cada EVA.

La contraseña se genera al crear la instalación, se guarda cifrada en la base
administrativa y se puede consultar/regenerar desde el panel. El valor en claro
solo se devuelve a usuarios con permiso de gestión de instalaciones.
"""

import secrets
import string

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.core.config import get_settings
from app.models.client import Client
from app.models.infrastructure import Domain, Installation
from app.services import audit, eva_users, secrets_service
from app.services.util import as_uuid

EMAIL_KEY = "EVA_ADMIN_EMAIL"
PASSWORD_KEY = "EVA_ADMIN_PASSWORD"


def _generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _default_email(db: Session, installation: Installation, client: Client) -> str:
    domain = db.scalar(
        select(Domain).where(
            Domain.installation_id == installation.id,
            Domain.kind == "primary",
        )
    )
    if domain:
        return f"admin@{domain.fqdn}"
    settings = get_settings()
    ref = client.slug or installation.id.hex[:8]
    return f"admin@{ref}.{settings.public_domain_suffix}"


def get_access(db: Session, installation_id: str) -> dict:
    return {
        "email": secrets_service.get_value(db, installation_id, EMAIL_KEY),
        "password": secrets_service.get_value(db, installation_id, PASSWORD_KEY),
    }


def ensure_access(db: Session, context: AuthContext, installation: Installation, client: Client) -> dict:
    existing = get_access(db, str(installation.id))
    if existing["email"] and existing["password"]:
        return existing

    email = existing["email"] or _default_email(db, installation, client)
    password = _generate_password()
    try:
        eva_users.create_user(db, context, str(installation.id), email, password, "Administrador", "admin")
    except ValueError as exc:
        if "ya existe" not in str(exc):
            raise
        eva_users.reset_password_by_email(db, context, str(installation.id), email, password)

    secrets_service.set_value(db, str(installation.id), EMAIL_KEY, email)
    secrets_service.set_value(db, str(installation.id), PASSWORD_KEY, password)
    audit.record(db, context, "installation.access.create", "installation", installation.id, email=email)
    db.commit()
    return {"email": email, "password": password}


def reset_access(db: Session, context: AuthContext, installation_id: str) -> dict:
    installation = db.get(Installation, as_uuid(installation_id))
    if installation is None:
        raise LookupError("instalación no encontrada")
    client = db.get(Client, installation.client_id)
    if client is None:
        raise LookupError("cliente no encontrado")

    email = secrets_service.get_value(db, installation_id, EMAIL_KEY) or _default_email(
        db, installation, client
    )
    password = _generate_password()
    try:
        eva_users.reset_password_by_email(db, context, installation_id, email, password)
    except LookupError:
        eva_users.create_user(db, context, installation_id, email, password, "Administrador", "admin")

    secrets_service.set_value(db, installation_id, EMAIL_KEY, email)
    secrets_service.set_value(db, installation_id, PASSWORD_KEY, password)
    audit.record(db, context, "installation.access.reset", "installation", installation.id, email=email)
    db.commit()
    return {"email": email, "password": password}
