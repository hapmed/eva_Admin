"""Usuarios internos de cada app EVA (gestión por acceso directo a la BD).

Convención de la EVA (ver docs/EVAS_APPS/REQUISITOS_EVA.md):

    tabla `app_users`
      id            uuid pk
      email         text unique
      password_hash text   (bcrypt, prefijo $2)
      full_name     text
      role          text
      is_active     boolean
      created_at    timestamptz

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

TABLE = "app_users"


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
    with _connect(record) as connection, connection.cursor() as cursor:
        try:
            cursor.execute(
                f"SELECT id, email, full_name, role, is_active, created_at FROM {TABLE} ORDER BY created_at"
            )
        except psycopg.errors.UndefinedTable as exc:
            raise ValueError("la EVA no expone la tabla 'app_users'") from exc
        return [_row(row) for row in cursor.fetchall()]


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
    user_id = uuid.uuid4()
    with _connect(record) as connection, connection.cursor() as cursor:
        try:
            cursor.execute(
                f"INSERT INTO {TABLE} (id, email, password_hash, full_name, role, is_active, created_at) "
                f"VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (str(user_id), email, hash_password(password), full_name, role, True, datetime.now(UTC)),
            )
        except psycopg.errors.UndefinedTable as exc:
            raise ValueError("la EVA no expone la tabla 'app_users'") from exc
        except psycopg.errors.UniqueViolation as exc:
            raise ValueError("ya existe un usuario con ese correo") from exc
    audit.record(db, context, "eva_user.create", "installation", installation_id, email=email)
    db.commit()
    return {
        "id": str(user_id),
        "email": email,
        "full_name": full_name,
        "role": role,
        "is_active": True,
        "created_at": None,
    }


def reset_password(
    db: Session, context: AuthContext, installation_id: str, user_id: str, password: str
) -> None:
    record = _record_for_installation(db, installation_id)
    with _connect(record) as connection, connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE {TABLE} SET password_hash = %s WHERE id = %s",
            (hash_password(password), user_id),
        )
        if cursor.rowcount == 0:
            raise LookupError("usuario no encontrado")
    audit.record(db, context, "eva_user.reset_password", "installation", installation_id, user_id=user_id)
    db.commit()


def delete_user(db: Session, context: AuthContext, installation_id: str, user_id: str) -> None:
    record = _record_for_installation(db, installation_id)
    with _connect(record) as connection, connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {TABLE} WHERE id = %s", (user_id,))
        if cursor.rowcount == 0:
            raise LookupError("usuario no encontrado")
    audit.record(db, context, "eva_user.delete", "installation", installation_id, user_id=user_id)
    db.commit()
