"""Lógica de usuarios internos, roles y permisos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.core.security import hash_password
from app.models.user import HapmedUser, Permission, Role
from app.schemas.user import UserCreate, UserUpdate
from app.services import audit
from app.services.util import as_uuid


def _resolve_roles(db: Session, codes: list[str]) -> list[Role]:
    if not codes:
        return []
    roles = list(db.scalars(select(Role).where(Role.code.in_(codes))).all())
    missing = set(codes) - {role.code for role in roles}
    if missing:
        raise ValueError(f"roles desconocidos: {', '.join(sorted(missing))}")
    return roles


def list_users(db: Session) -> list[HapmedUser]:
    return list(db.scalars(select(HapmedUser).order_by(HapmedUser.created_at)).all())


def get_user(db: Session, user_id: str) -> HapmedUser:
    user = db.get(HapmedUser, as_uuid(user_id))
    if user is None:
        raise LookupError("usuario no encontrado")
    return user


def create_user(db: Session, context: AuthContext, data: UserCreate) -> HapmedUser:
    if db.scalar(select(HapmedUser).where(HapmedUser.email == data.email)):
        raise ValueError("el correo ya está registrado")
    user = HapmedUser(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )
    user.roles = _resolve_roles(db, data.roles)
    db.add(user)
    db.flush()
    audit.record(db, context, "user.create", "hapmed_user", user.id, email=user.email)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, context: AuthContext, user_id: str, data: UserUpdate) -> HapmedUser:
    user = get_user(db, user_id)
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.is_active is not None:
        user.is_active = data.is_active
    audit.record(db, context, "user.update", "hapmed_user", user.id)
    db.commit()
    db.refresh(user)
    return user


def set_roles(db: Session, context: AuthContext, user_id: str, codes: list[str]) -> HapmedUser:
    if str(user_id) == context.actor_id:
        raise ValueError("no puedes cambiar tus propios roles")
    user = get_user(db, user_id)
    user.roles = _resolve_roles(db, codes)
    audit.record(db, context, "user.set_roles", "hapmed_user", user.id, roles=",".join(sorted(codes)))
    db.commit()
    db.refresh(user)
    return user


def set_active(db: Session, context: AuthContext, user_id: str, active: bool) -> HapmedUser:
    if str(user_id) == context.actor_id:
        raise ValueError("no puedes cambiar tu propio estado")
    user = get_user(db, user_id)
    user.is_active = active
    audit.record(
        db,
        context,
        "user.activate" if active else "user.deactivate",
        "hapmed_user",
        user.id,
    )
    db.commit()
    db.refresh(user)
    return user


def list_roles(db: Session) -> list[Role]:
    return list(db.scalars(select(Role).order_by(Role.code)).all())


def list_permissions(db: Session) -> list[Permission]:
    return list(db.scalars(select(Permission).order_by(Permission.code)).all())


def set_role_permissions(db: Session, context: AuthContext, role_id: str, codes: list[str]) -> Role:
    role = db.get(Role, as_uuid(role_id))
    if role is None:
        raise LookupError("rol no encontrado")
    permissions = list(db.scalars(select(Permission).where(Permission.code.in_(codes))).all())
    missing = set(codes) - {permission.code for permission in permissions}
    if missing:
        raise ValueError(f"permisos desconocidos: {', '.join(sorted(missing))}")
    role.permissions = permissions
    audit.record(
        db,
        context,
        "role.set_permissions",
        "role",
        role.id,
        permissions=",".join(sorted(codes)),
    )
    db.commit()
    db.refresh(role)
    return role
