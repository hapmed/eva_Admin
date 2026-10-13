"""Valores de secretos por instalación (cifrados) para inyectar en el despliegue.

Los valores en claro nunca se guardan ni se registran. Cada secreto declarado en
la instalación (`SecretReference`) obtiene un valor generado una sola vez y se
reutiliza en cada despliegue/actualización, de modo que secretos como
`JWT_SECRET` permanecen estables entre reinicios.
"""

import base64
import hashlib
import secrets

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.infrastructure import InstallationSecret, SecretReference
from app.services.util import as_uuid


def _fernet() -> Fernet:
    settings = get_settings()
    if settings.secret_encryption_key:
        key = settings.secret_encryption_key.encode("utf-8")
    else:
        digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def get_or_create_value(db: Session, installation_id, key: str) -> str:
    row = db.scalar(
        select(InstallationSecret).where(
            InstallationSecret.installation_id == as_uuid(installation_id),
            InstallationSecret.key == key,
        )
    )
    if row is not None:
        return _fernet().decrypt(row.value_encrypted.encode("utf-8")).decode("utf-8")
    value = secrets.token_urlsafe(32)
    db.add(
        InstallationSecret(
            installation_id=as_uuid(installation_id),
            key=key,
            value_encrypted=_fernet().encrypt(value.encode("utf-8")).decode("utf-8"),
        )
    )
    db.flush()
    return value


def env_for(db: Session, installation_id) -> dict[str, str]:
    """Devuelve {KEY: valor} para todos los secretos declarados en la instalación."""
    references = db.scalars(
        select(SecretReference)
        .where(SecretReference.installation_id == as_uuid(installation_id))
        .order_by(SecretReference.key)
    ).all()
    return {
        reference.key: get_or_create_value(db, installation_id, reference.key) for reference in references
    }
