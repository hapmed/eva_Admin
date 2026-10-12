"""Roles y permisos."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import permission_out, role_out
from app.db.session import get_db
from app.schemas.user import PermissionOut, RoleOut, RolePermissionsUpdate
from app.services import user_service

router = APIRouter()


@router.get("/roles", response_model=list[RoleOut])
def list_roles(
    _: AuthContext = Depends(require_permission("roles:read")), db: Session = Depends(get_db)
) -> list[dict]:
    return [role_out(role) for role in user_service.list_roles(db)]


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(
    _: AuthContext = Depends(require_permission("roles:read")), db: Session = Depends(get_db)
) -> list[dict]:
    return [permission_out(permission) for permission in user_service.list_permissions(db)]


@router.put("/roles/{role_id}/permissions", response_model=RoleOut)
def set_role_permissions(
    role_id: str,
    data: RolePermissionsUpdate,
    context: AuthContext = Depends(require_permission("roles:manage")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        role = user_service.set_role_permissions(db, context, role_id, data.permissions)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return role_out(role)
