"""Usuarios internos de cada app EVA (gestión por acceso directo a la BD).

Soporta dos contratos de tabla:

- `app_users` (contrato EVAS Admin): id uuid, full_name, role, is_active.
- `usuario` (EVAs HAPMED Admon): id serial, nombre, rol, activo.

EVAS Admin se conecta a la base del cliente con las credenciales de
administración del aprovisionamiento (no se guardan credenciales por cliente).
"""

import uuid
from datetime import UTC, datetime

import bcrypt
import psycopg
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.core.config import get_settings
from app.models.infrastructure import DatabaseRecord
from app.services import audit
from app.services.util import as_uuid


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _record_for_installation(db: Session, installation_id: str) -> DatabaseRecord:
    record = db.scalar(
        select(DatabaseRecord).where(DatabaseRecord.installation_id == as_uuid(installation_id))
    )
    if record is None:
        raise LookupError("la instalación no tiene base de datos asociada")
    return record


def _connect(record: DatabaseRecord) -> psycopg.Connection:
    settings = get_settings()
    if not settings.provision_enabled or not settings.provision_db_admin_user:
        raise RuntimeError("acceso a la base de datos del cliente no configurado")
    return psycopg.connect(
        host=settings.provision_db_host,
        port=settings.provision_db_port,
        user=settings.provision_db_admin_user,
        password=settings.provision_db_admin_password,
        dbname=record.logical_name,
        autocommit=True,
    )


def _schema(connection: psycopg.Connection) -> dict[str, str]:
    row = connection.execute(
        "SELECT to_regclass('public.app_users'), to_regclass('public.usuario')"
    ).fetchone()
    if row and row[0]:
        return {
            "table": "app_users",
            "id_type": "uuid",
            "select": (
                "SELECT id, email, full_name, role, is_active, created_at FROM app_users ORDER BY created_at"
            ),
            "insert": (
                "INSERT INTO app_users "
                "(id, email, password_hash, full_name, role, is_active, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"
            ),
            "update": "UPDATE app_users SET password_hash = %s WHERE id = %s",
            "update_email": "UPDATE app_users SET password_hash = %s WHERE lower(email) = lower(%s)",
            "delete": "DELETE FROM app_users WHERE id = %s",
        }
    if row and row[1]:
        return {
            "table": "usuario",
            "id_type": "int",
            "select": (
                "SELECT id, email, nombre AS full_name, rol AS role, activo AS is_active, "
                "created_at FROM usuario ORDER BY created_at"
            ),
            "insert": (
                "INSERT INTO usuario (email, password_hash, nombre, rol, activo) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id"
            ),
            "update": "UPDATE usuario SET password_hash = %s WHERE id = %s",
            "update_email": "UPDATE usuario SET password_hash = %s WHERE lower(email) = lower(%s)",
            "delete": "DELETE FROM usuario WHERE id = %s",
        }
    raise ValueError("la EVA no expone una tabla de usuarios compatible")


def _row(row) -> dict:
    return {
        "id": str(row[0]),
        "email": row[1],
        "full_name": row[2] or "",
        "role": row[3] or "",
        "is_active": bool(row[4]),
        "created_at": row[5].isoformat() if row[5] else None,
    }


def list_users(db: Session, installation_id: str) -> list[dict]:
    record = _record_for_installation(db, installation_id)
    with _connect(record) as connection:
        info = _schema(connection)
        try:
            rows = connection.execute(info["select"]).fetchall()
        except psycopg.errors.UndefinedTable as exc:
            raise ValueError("la EVA no expone una tabla de usuarios compatible") from exc
        return [_row(row) for row in rows]


def create_user(
    db: Session,
    context: AuthContext,
    installation_id: str,
    email: str,
    password: str,
    full_name: str,
    role: str,
) -> dict:
    record = _record_for_installation(db, installation_id)
    user_id: str
    with _connect(record) as connection:
        info = _schema(connection)
        try:
            if info["id_type"] == "uuid":
                user_id = str(uuid.uuid4())
                connection.execute(
                    info["insert"],
                    (
                        user_id,
                        email.lower(),
                        hash_password(password),
                        full_name,
                        role,
                        True,
                        datetime.now(UTC),
                    ),
                )
            else:
                row = connection.execute(
                    info["insert"],
                    (email.lower(), hash_password(password), full_name, role, True),
                ).fetchone()
                if row is None:
                    raise RuntimeError("no se pudo crear el usuario")
                user_id = str(row[0])
        except psycopg.errors.UndefinedTable as exc:
            raise ValueError("la EVA no expone una tabla de usuarios compatible") from exc
        except psycopg.errors.UniqueViolation as exc:
            raise ValueError("ya existe un usuario con ese correo") from exc
    audit.record(db, context, "eva_user.create", "installation", installation_id, email=email)
    db.commit()
    return {
        "id": user_id,
        "email": email.lower(),
        "full_name": full_name,
        "role": role,
        "is_active": True,
        "created_at": None,
    }


def reset_password(
    db: Session, context: AuthContext, installation_id: str, user_id: str, password: str
) -> None:
    record = _record_for_installation(db, installation_id)
    with _connect(record) as connection:
        info = _schema(connection)
        id_value = uuid.UUID(user_id) if info["id_type"] == "uuid" else int(user_id)
        cursor = connection.execute(info["update"], (hash_password(password), id_value))
        if cursor.rowcount == 0:
            raise LookupError("usuario no encontrado")
    audit.record(db, context, "eva_user.reset_password", "installation", installation_id, user_id=user_id)
    db.commit()


def reset_password_by_email(
    db: Session, context: AuthContext, installation_id: str, email: str, password: str
) -> None:
    record = _record_for_installation(db, installation_id)
    with _connect(record) as connection:
        info = _schema(connection)
        cursor = connection.execute(info["update_email"], (hash_password(password), email.lower()))
        if cursor.rowcount == 0:
            raise LookupError("usuario no encontrado")
    audit.record(db, context, "eva_user.reset_password", "installation", installation_id, email=email)
    db.commit()


def delete_user(db: Session, context: AuthContext, installation_id: str, user_id: str) -> None:
    record = _record_for_installation(db, installation_id)
    with _connect(record) as connection:
        info = _schema(connection)
        id_value = uuid.UUID(user_id) if info["id_type"] == "uuid" else int(user_id)
        cursor = connection.execute(info["delete"], (id_value,))
        if cursor.rowcount == 0:
            raise LookupError("usuario no encontrado")
    audit.record(db, context, "eva_user.delete", "installation", installation_id, user_id=user_id)
    db.commit()
