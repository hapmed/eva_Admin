"""Bootstrap: creación del primer administrador (idempotente)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import HapmedUser, Role


def ensure_superadmin(db: Session, email: str, password: str) -> HapmedUser | None:
    if not email or not password:
        return None
    existing = db.scalar(select(HapmedUser).where(HapmedUser.email == email))
    if existing is not None:
        return existing
    user = HapmedUser(
        email=email,
        full_name="Administrador",
        password_hash=hash_password(password),
        is_active=True,
    )
    role = db.scalar(select(Role).where(Role.code == "superadmin"))
    if role is not None:
        user.roles = [role]
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
