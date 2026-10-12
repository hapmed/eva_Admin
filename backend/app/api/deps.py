"""Dependencias de autenticación y autorización (auth dual, ADR-009).

- Web: cookie de sesión firmada + CSRF en métodos que mutan estado.
- Integraciones/agente: token Bearer.
"""

import hmac
import uuid

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.core.config import get_settings
from app.core.security import hash_token
from app.core.session import verify_session_token
from app.db.session import get_db
from app.models.token import ApiToken
from app.models.user import HapmedUser

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _bearer_context(raw_token: str, db: Session) -> AuthContext | None:
    token = db.scalar(
        select(ApiToken).where(
            ApiToken.token_hash == hash_token(raw_token),
            ApiToken.status == "active",
        )
    )
    if token is None:
        return None
    return AuthContext(
        actor_type=token.owner_type,
        actor_id=str(token.id),
        method="bearer",
        permissions=set(token.scopes or []),
    )


def _cookie_context(request: Request, db: Session) -> AuthContext | None:
    settings = get_settings()
    raw = request.cookies.get(settings.session_cookie_name)
    if not raw:
        return None
    user_id = verify_session_token(raw)
    if not user_id:
        return None
    try:
        user = db.get(HapmedUser, uuid.UUID(user_id))
    except ValueError:
        return None
    if user is None or not user.is_active:
        return None
    permissions = {p.code for role in user.roles for p in role.permissions}
    return AuthContext(
        actor_type="hapmed_user",
        actor_id=str(user.id),
        method="cookie",
        permissions=permissions,
    )


def _enforce_csrf(request: Request) -> None:
    settings = get_settings()
    cookie = request.cookies.get(settings.csrf_cookie_name)
    header = request.headers.get("x-csrf-token")
    if not cookie or not header or not hmac.compare_digest(cookie, header):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF inválido")


def get_auth_context(request: Request, db: Session = Depends(get_db)) -> AuthContext:
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        context = _bearer_context(authorization[7:].strip(), db)
        if context is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token inválido")
        return context

    context = _cookie_context(request, db)
    if context is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no autenticado")
    if request.method in MUTATING_METHODS:
        _enforce_csrf(request)
    return context


def require_permission(code: str):
    def checker(context: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if code not in context.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"falta el permiso {code}",
            )
        return context

    return checker
