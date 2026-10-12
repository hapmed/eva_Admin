"""Utilidades WebAuthn: RP ID y origin derivados de la petición (por dominio)."""

import base64

from fastapi import Request

from app.core.config import get_settings


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def rp_id(request: Request) -> str:
    """Relying Party ID = dominio del host actual (permite multi-dominio por cliente)."""
    settings = get_settings()
    if settings.webauthn_rp_id:
        return settings.webauthn_rp_id
    host = request.headers.get("host") or request.url.netloc
    return host.split(":")[0]


def origin(request: Request) -> str:
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
    host = request.headers.get("host") or request.url.netloc
    return f"{scheme}://{host}"
