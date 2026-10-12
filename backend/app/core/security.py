"""Utilidades de seguridad (hashing de contraseñas y tokens).

Fase 2 usa `hashlib.scrypt` (estándar, sin dependencias externas). La decisión
ADR-009 admite Argon2id/bcrypt; se adoptará un KDF dedicado (argon2-cffi) al
implementar autenticación real en Fase 3. Nunca se guardan valores en claro.
"""

import hashlib
import hmac
import os

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_DKLEN = 32


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    if not password:
        raise ValueError("password vacío")
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_DKLEN,
    )
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    if algo != "scrypt":
        return False
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt_hex),
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_DKLEN,
    )
    return hmac.compare_digest(digest.hex(), digest_hex)


def hash_token(token: str) -> str:
    """Hash determinista para API tokens (sólo se guarda el hash)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
