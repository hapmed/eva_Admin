"""Aprovisionamiento real: puerto de host, nombre de contenedor y base de datos
por cliente en el PostgreSQL existente.

Nunca se guarda la contraseña de la base: se genera en cada despliegue y se
inyecta al contenedor por variable de entorno.
"""

import re
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.infrastructure import Installation


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]", "", value.lower())
    return cleaned or "x"


def allocate_port(db: Session) -> int:
    settings = get_settings()
    used = {
        port
        for (port,) in db.execute(
            select(Installation.host_port).where(Installation.host_port.is_not(None))
        ).all()
    }
    for port in range(settings.port_range_start, settings.port_range_end + 1):
        if port not in used:
            return port
    raise ValueError("sin puertos libres en el rango configurado")


def container_name(client_ref: str, eva_code: str) -> str:
    return f"eva_{_slug(client_ref)}_{_slug(eva_code)}"[:120]


def database_names(client_ref: str, eva_code: str) -> tuple[str, str]:
    settings = get_settings()
    base = f"{settings.provision_user_prefix}_{_slug(client_ref)}_{_slug(eva_code)}"[:50]
    return base, base


def deprovision_database(db_name: str) -> None:
    """Elimina la base y el rol de una instalación (operación destructiva)."""
    settings = get_settings()
    if not settings.provision_enabled or not settings.provision_db_admin_user:
        raise RuntimeError("aprovisionamiento de base de datos deshabilitado")

    prefix = f"{settings.provision_user_prefix}_"
    if not db_name.startswith(prefix):
        raise ValueError("la base no está gestionada por EVAS Admin")

    import psycopg
    from psycopg import sql

    admin_dsn = (
        f"host={settings.provision_db_host} port={settings.provision_db_port} "
        f"user={settings.provision_db_admin_user} password={settings.provision_db_admin_password} "
        f"dbname={settings.provision_db_admin_db}"
    )
    with psycopg.connect(admin_dsn, autocommit=True) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = %s AND pid <> pg_backend_pid()",
            (db_name,),
        )
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cursor.fetchone():
            cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(db_name)))
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_name,))
        if cursor.fetchone():
            cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(db_name)))


def provision_database(client_ref: str, eva_code: str) -> tuple[str, str, str]:
    """Crea/actualiza rol+base para el cliente. Devuelve (db_name, db_user, url)."""
    settings = get_settings()
    if not settings.provision_enabled or not settings.provision_db_admin_user:
        raise RuntimeError("aprovisionamiento de base de datos deshabilitado")

    import psycopg
    from psycopg import sql

    db_name, db_user = database_names(client_ref, eva_code)
    password = secrets.token_urlsafe(24)

    admin_dsn = (
        f"host={settings.provision_db_host} port={settings.provision_db_port} "
        f"user={settings.provision_db_admin_user} password={settings.provision_db_admin_password} "
        f"dbname={settings.provision_db_admin_db}"
    )
    with psycopg.connect(admin_dsn, autocommit=True) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
        if cursor.fetchone():
            cursor.execute(
                sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD {}").format(
                    sql.Identifier(db_user), sql.Literal(password)
                )
            )
        else:
            cursor.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(db_user), sql.Literal(password)
                )
            )
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not cursor.fetchone():
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(db_name), sql.Identifier(db_user)
                )
            )

    database_url = (
        f"postgresql+psycopg://{db_user}:{password}"
        f"@{settings.provision_db_host}:{settings.provision_db_port}/{db_name}"
    )
    return db_name, db_user, database_url
