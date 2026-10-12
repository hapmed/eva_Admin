"""Sesión firmada (cookie) y tokens CSRF.

La cookie de sesión es un valor firmado con HMAC (sin dependencias externas).
Contiene el id del usuario y su expiración. No guarda datos sensibles.
"""

import base64
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from app.core.config import get_settings


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64d(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(secret: str, body: str) -> str:
    return hmac.new(secret.encode(), body.encode(), sha256).hexdigest()


def create_session_token(user_id: str) -> str:
    settings = get_settings()
    expires = datetime.now(UTC) + timedelta(minutes=settings.session_ttl_minutes)
    payload = json.dumps({"sub": user_id, "exp": expires.isoformat()}).encode()
    body = _b64e(payload)
    return f"{body}.{_sign(settings.secret_key, body)}"


def verify_session_token(token: str) -> str | None:
    settings = get_settings()
    try:
        body, signature = token.split(".", 1)
    except ValueError:
        return None
    if not hmac.compare_digest(signature, _sign(settings.secret_key, body)):
        return None
    try:
        data = json.loads(_b64d(body))
        expires = datetime.fromisoformat(data["exp"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None
    if expires < datetime.now(UTC):
        return None
    return str(data["sub"])


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)
