"""Autenticación y sesión (auth dual, ADR-009)."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_auth_context
from app.core.auth import AuthContext
from app.core.config import get_settings
from app.core.rate_limit import rate_limit
from app.core.security import verify_password
from app.core.session import create_session_token, new_csrf_token
from app.db.session import get_db
from app.models.user import HapmedUser
from app.schemas.auth import CsrfResponse, LoginRequest, MeResponse

router = APIRouter()


def _me_from_user(user: HapmedUser) -> MeResponse:
    permissions = sorted({p.code for role in user.roles for p in role.permissions})
    return MeResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=sorted(role.code for role in user.roles),
        permissions=permissions,
    )


def _set_cookie(response: Response, name: str, value: str, *, http_only: bool) -> None:
    settings = get_settings()
    response.set_cookie(
        name,
        value,
        secure=settings.session_cookie_secure,
        httponly=http_only,
        samesite=settings.session_cookie_samesite,
        path="/",
    )


@router.get("/csrf", response_model=CsrfResponse)
def get_csrf(response: Response) -> CsrfResponse:
    settings = get_settings()
    token = new_csrf_token()
    _set_cookie(response, settings.csrf_cookie_name, token, http_only=False)
    return CsrfResponse(csrf_token=token)


@router.post("/login", response_model=MeResponse, dependencies=[Depends(rate_limit("auth"))])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> MeResponse:
    settings = get_settings()
    user = db.scalar(select(HapmedUser).where(HapmedUser.email == payload.email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="credenciales inválidas")

    user.last_login_at = datetime.now(UTC)
    db.commit()

    _set_cookie(response, settings.session_cookie_name, create_session_token(str(user.id)), http_only=True)
    _set_cookie(response, settings.csrf_cookie_name, new_csrf_token(), http_only=False)
    return _me_from_user(user)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    settings = get_settings()
    response.delete_cookie(settings.session_cookie_name, path="/")
    response.delete_cookie(settings.csrf_cookie_name, path="/")
    return {"status": "ok"}


@router.get("/me", response_model=MeResponse)
def me(context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> MeResponse:
    if context.actor_type == "hapmed_user":
        user = db.get(HapmedUser, uuid.UUID(context.actor_id))
        if user is not None:
            return _me_from_user(user)
    return MeResponse(
        id=context.actor_id,
        email="",
        full_name="",
        roles=[],
        permissions=sorted(context.permissions),
    )
