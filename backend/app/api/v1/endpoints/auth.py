"""Autenticación, sesión, contraseña y passkeys (auth dual, ADR-009)."""

import json
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from webauthn.helpers import options_to_json

from app.api.deps import get_auth_context
from app.core import webauthn as wa
from app.core.auth import AuthContext
from app.core.config import get_settings
from app.core.rate_limit import rate_limit
from app.core.security import hash_password, verify_password
from app.core.session import create_session_token, create_token, new_csrf_token, read_token
from app.db.session import get_db
from app.models.user import HapmedUser
from app.schemas.auth import (
    CredentialOut,
    CsrfResponse,
    LoginRequest,
    MeResponse,
    PasswordChange,
    WebAuthnLoginBegin,
    WebAuthnLoginComplete,
    WebAuthnRegisterComplete,
)
from app.services import audit, webauthn_service

router = APIRouter()

CHALLENGE_COOKIE = "evas_wa_challenge"


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


def _current_user(db: Session, context: AuthContext) -> HapmedUser:
    if context.actor_type != "hapmed_user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="solo los usuarios pueden gestionar passkeys",
        )
    user = db.get(HapmedUser, uuid.UUID(context.actor_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="usuario no encontrado")
    return user


def _me_from_user(user: HapmedUser, db: Session, passkey_name: str | None = None) -> MeResponse:
    permissions = sorted({p.code for role in user.roles for p in role.permissions})
    return MeResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=sorted(role.code for role in user.roles),
        permissions=permissions,
        passkey_name=passkey_name,
        has_passkeys=webauthn_service.count_credentials(db, user.id) > 0,
    )


def _credential_out(credential) -> dict:
    return {
        "id": str(credential.id),
        "name": credential.name,
        "created_at": credential.created_at,
        "last_used_at": credential.last_used_at,
    }


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
    return _me_from_user(user, db)


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
            return _me_from_user(user, db, context.passkey_name)
    return MeResponse(
        id=context.actor_id,
        email="",
        full_name="",
        roles=[],
        permissions=sorted(context.permissions),
        passkey_name=context.passkey_name,
        has_passkeys=False,
    )


@router.post("/password/change")
def change_password(
    data: PasswordChange,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    user = _current_user(db, context)
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="la contraseña actual no es correcta"
        )
    user.password_hash = hash_password(data.new_password)
    audit.record(db, context, "user.password_change", "hapmed_user", user.id)
    db.commit()
    return {"status": "ok"}


@router.post("/webauthn/register/begin")
def webauthn_register_begin(
    request: Request,
    response: Response,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> dict:
    user = _current_user(db, context)
    options = webauthn_service.register_begin(db, user, wa.rp_id(request), get_settings().webauthn_rp_name)
    _set_cookie(
        response,
        CHALLENGE_COOKIE,
        create_token({"ch": wa.b64url_encode(options.challenge), "p": "reg"}, 5),
        http_only=True,
    )
    return json.loads(options_to_json(options))


@router.post("/webauthn/register/complete", response_model=CredentialOut)
def webauthn_register_complete(
    data: WebAuthnRegisterComplete,
    request: Request,
    response: Response,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> dict:
    user = _current_user(db, context)
    claims = read_token(request.cookies.get(CHALLENGE_COOKIE) or "")
    if not claims or claims.get("p") != "reg":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="challenge no válido")
    challenge = wa.b64url_decode(claims["ch"])
    try:
        credential = webauthn_service.register_complete(
            db, context, user, data.credential, challenge, wa.rp_id(request), wa.origin(request), data.name
        )
    except Exception as exc:  # noqa: BLE001 - mensaje genérico
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="no se pudo registrar la passkey"
        ) from exc
    response.delete_cookie(CHALLENGE_COOKIE, path="/")
    return _credential_out(credential)


@router.post("/webauthn/login/begin", dependencies=[Depends(rate_limit("auth"))])
def webauthn_login_begin(
    data: WebAuthnLoginBegin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    options = webauthn_service.login_begin(db, wa.rp_id(request), data.email)
    _set_cookie(
        response,
        CHALLENGE_COOKIE,
        create_token({"ch": wa.b64url_encode(options.challenge), "p": "auth"}, 5),
        http_only=True,
    )
    return json.loads(options_to_json(options))


@router.post(
    "/webauthn/login/complete", response_model=MeResponse, dependencies=[Depends(rate_limit("auth"))]
)
def webauthn_login_complete(
    data: WebAuthnLoginComplete, request: Request, response: Response, db: Session = Depends(get_db)
) -> MeResponse:
    settings = get_settings()
    claims = read_token(request.cookies.get(CHALLENGE_COOKIE) or "")
    if not claims or claims.get("p") != "auth":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="challenge no válido")
    challenge = wa.b64url_decode(claims["ch"])
    try:
        user, credential = webauthn_service.login_complete(
            db, data.credential, challenge, wa.rp_id(request), wa.origin(request)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="passkey no válida") from exc

    user.last_login_at = datetime.now(UTC)
    db.commit()
    _set_cookie(
        response,
        settings.session_cookie_name,
        create_session_token(str(user.id), credential.name),
        http_only=True,
    )
    _set_cookie(response, settings.csrf_cookie_name, new_csrf_token(), http_only=False)
    response.delete_cookie(CHALLENGE_COOKIE, path="/")
    return _me_from_user(user, db, credential.name)


@router.get("/webauthn/credentials", response_model=list[CredentialOut])
def list_webauthn_credentials(
    context: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)
) -> list[dict]:
    user = _current_user(db, context)
    return [_credential_out(credential) for credential in webauthn_service.list_credentials(db, user.id)]


@router.delete("/webauthn/credentials/{credential_id}", status_code=204)
def delete_webauthn_credential(
    credential_id: str,
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> None:
    user = _current_user(db, context)
    try:
        webauthn_service.delete_credential(db, context, user.id, credential_id)
    except (ValueError, LookupError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
