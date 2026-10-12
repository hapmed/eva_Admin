"""Sesión firmada (cookie), tokens CSRF y challenges WebAuthn.

La cookie de sesión es un valor firmado con HMAC (sin dependencias externas).
Contiene el id del usuario, opcionalmente el nombre del passkey usado y su
expiración. No guarda datos sensibles.
"""

import base64
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any

from app.core.config import get_settings


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64d(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(secret: str, body: str) -> str:
    return hmac.new(secret.encode(), body.encode(), sha256).hexdigest()


def create_token(claims: dict[str, Any], ttl_minutes: int) -> str:
    settings = get_settings()
    payload = {
        **claims,
        "exp": (datetime.now(UTC) + timedelta(minutes=ttl_minutes)).isoformat(),
    }
    body = _b64e(json.dumps(payload).encode())
    return f"{body}.{_sign(settings.secret_key, body)}"


def read_token(token: str) -> dict[str, Any] | None:
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
    return data


def create_session_token(user_id: str, passkey_name: str | None = None) -> str:
    claims: dict[str, Any] = {"sub": user_id}
    if passkey_name:
        claims["wa"] = passkey_name
    return create_token(claims, get_settings().session_ttl_minutes)


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)
