"""Catálogo de permisos y roles, y sembrado inicial."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.infrastructure import Node
from app.models.user import Permission, Role

PERMISSIONS: dict[str, str] = {
    "users:read": "Ver usuarios internos",
    "users:write": "Crear y editar usuarios internos",
    "roles:read": "Ver roles y permisos",
    "roles:manage": "Gestionar roles y permisos",
    "clients:read": "Ver clientes",
    "clients:write": "Crear y editar clientes",
    "evas:read": "Ver catálogo EVA",
    "evas:manage": "Gestionar catálogo EVA",
    "plans:read": "Ver planes",
    "plans:manage": "Gestionar planes",
    "subscriptions:read": "Ver suscripciones",
    "subscriptions:write": "Gestionar suscripciones",
    "installations:read": "Ver instalaciones",
    "installations:write": "Gestionar instalaciones",
    "installations:operate": "Operar instalaciones",
    "installations:upgrade": "Actualizar instalaciones",
    "domains:read": "Ver dominios",
    "domains:write": "Gestionar dominios",
    "databases:read": "Ver metadatos de bases de datos",
    "databases:write": "Gestionar metadatos de bases de datos",
    "backups:request": "Solicitar copias de seguridad",
    "backups:restore": "Solicitar restauración",
    "operations:read": "Ver operaciones y registros",
    "audit:read": "Ver auditoría",
    "alerts:read": "Ver alertas",
    "alerts:write": "Gestionar alertas",
    "tokens:read": "Ver tokens de integración",
    "tokens:manage": "Gestionar tokens de integración",
}

READ_ONLY: set[str] = {code for code in PERMISSIONS if code.endswith(":read")}

ROLE_DEFINITIONS: dict[str, tuple[str, set[str]]] = {
    "superadmin": ("Superadministrador", set(PERMISSIONS)),
    "operations": (
        "Operaciones",
        {
            "clients:read",
            "evas:read",
            "plans:read",
            "subscriptions:read",
            "subscriptions:write",
            "installations:read",
            "installations:write",
            "installations:operate",
            "installations:upgrade",
            "domains:read",
            "domains:write",
            "databases:read",
            "databases:write",
            "backups:request",
            "operations:read",
            "audit:read",
            "alerts:read",
        },
    ),
    "customer_care": (
        "Atención al cliente",
        {"clients:read", "subscriptions:read", "alerts:read", "audit:read"},
    ),
    "read_only": ("Solo lectura", READ_ONLY),
}


def seed(session: Session) -> None:
    """Crea permisos y roles si no existen. Idempotente."""
    existing = {p.code for p in session.scalars(select(Permission)).all()}
    for code, description in PERMISSIONS.items():
        if code not in existing:
            session.add(Permission(code=code, description=description))
    session.flush()

    permissions = {p.code: p for p in session.scalars(select(Permission)).all()}
    roles = {r.code: r for r in session.scalars(select(Role)).all()}
    for code, (name, codes) in ROLE_DEFINITIONS.items():
        role = roles.get(code)
        if role is None:
            role = Role(code=code, name=name, is_system=True)
            session.add(role)
        role.permissions = [permissions[perm_code] for perm_code in sorted(codes)]

    if session.scalar(select(Node).limit(1)) is None:
        session.add(Node(name="default", host_ref="local", environment="local", status="active"))
    session.commit()
