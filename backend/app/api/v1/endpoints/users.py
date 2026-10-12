"""Usuarios internos HAPMED."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import user_out
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, UserRolesUpdate, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("", response_model=list[UserOut])
def list_users(
    _: AuthContext = Depends(require_permission("users:read")), db: Session = Depends(get_db)
) -> list[dict]:
    return [user_out(user) for user in user_service.list_users(db)]


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    data: UserCreate,
    context: AuthContext = Depends(require_permission("users:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = user_service.create_user(db, context, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return user_out(user)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    _: AuthContext = Depends(require_permission("users:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = user_service.get_user(db, user_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return user_out(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    data: UserUpdate,
    context: AuthContext = Depends(require_permission("users:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = user_service.update_user(db, context, user_id, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return user_out(user)


@router.post("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: str,
    context: AuthContext = Depends(require_permission("users:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = user_service.set_active(db, context, user_id, False)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return user_out(user)


@router.post("/{user_id}/reactivate", response_model=UserOut)
def reactivate_user(
    user_id: str,
    context: AuthContext = Depends(require_permission("users:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = user_service.set_active(db, context, user_id, True)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return user_out(user)


@router.put("/{user_id}/roles", response_model=UserOut)
def set_user_roles(
    user_id: str,
    data: UserRolesUpdate,
    context: AuthContext = Depends(require_permission("roles:manage")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = user_service.set_roles(db, context, user_id, data.roles)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return user_out(user)
