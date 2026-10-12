"""Lógica de clientes y usuarios de cliente (aislamiento por cliente)."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.core.security import hash_password
from app.models.client import Client, ClientUser
from app.schemas.client import ClientCreate, ClientUpdate, ClientUserCreate, ClientUserUpdate
from app.services import audit
from app.services.util import as_uuid


def list_clients(db: Session, status: str | None = None, q: str | None = None) -> list[Client]:
    stmt = select(Client).order_by(Client.created_at)
    if status:
        stmt = stmt.where(Client.status == status)
    if q:
        stmt = stmt.where(Client.display_name.ilike(f"%{q}%"))
    return list(db.scalars(stmt).all())


def get_client(db: Session, client_id: str) -> Client:
    client = db.get(Client, as_uuid(client_id))
    if client is None:
        raise LookupError("cliente no encontrado")
    return client


def create_client(db: Session, context: AuthContext, data: ClientCreate) -> Client:
    client = Client(
        legal_name=data.legal_name,
        display_name=data.display_name,
        tax_id=data.tax_id,
        notes=data.notes,
        status="active",
    )
    db.add(client)
    db.flush()
    audit.record(db, context, "client.create", "client", client.id, name=client.display_name)
    db.commit()
    db.refresh(client)
    return client


def update_client(db: Session, context: AuthContext, client_id: str, data: ClientUpdate) -> Client:
    client = get_client(db, client_id)
    for field in ("legal_name", "display_name", "tax_id", "notes"):
        value = getattr(data, field)
        if value is not None:
            setattr(client, field, value)
    audit.record(db, context, "client.update", "client", client.id)
    db.commit()
    db.refresh(client)
    return client


def set_client_status(db: Session, context: AuthContext, client_id: str, status: str) -> Client:
    client = get_client(db, client_id)
    client.status = status
    if status == "archived":
        client.archived_at = datetime.now(UTC)
    audit.record(db, context, f"client.{status}", "client", client.id)
    db.commit()
    db.refresh(client)
    return client


def list_client_users(db: Session, client_id: str) -> list[ClientUser]:
    get_client(db, client_id)  # 404 si no existe
    client_uuid = as_uuid(client_id)
    return list(
        db.scalars(
            select(ClientUser).where(ClientUser.client_id == client_uuid).order_by(ClientUser.created_at)
        ).all()
    )


def create_client_user(
    db: Session, context: AuthContext, client_id: str, data: ClientUserCreate
) -> ClientUser:
    client = get_client(db, client_id)
    user = ClientUser(
        client_id=client.id,
        email=data.email,
        password_hash=hash_password(data.password),
        role_code=data.role_code,
    )
    db.add(user)
    db.flush()
    audit.record(db, context, "client_user.create", "client_user", user.id, client_id=str(client.id))
    db.commit()
    db.refresh(user)
    return user


def update_client_user(
    db: Session, context: AuthContext, client_id: str, user_id: str, data: ClientUserUpdate
) -> ClientUser:
    user = db.get(ClientUser, as_uuid(user_id))
    if user is None or str(user.client_id) != str(as_uuid(client_id)):
        raise LookupError("usuario de cliente no encontrado")
    if data.role_code is not None:
        user.role_code = data.role_code
    if data.is_active is not None:
        user.is_active = data.is_active
    audit.record(db, context, "client_user.update", "client_user", user.id)
    db.commit()
    db.refresh(user)
    return user
