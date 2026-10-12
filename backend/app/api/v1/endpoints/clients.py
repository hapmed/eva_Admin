"""Clientes y usuarios de cliente."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import client_out, client_user_out
from app.db.session import get_db
from app.schemas.client import (
    ClientCreate,
    ClientOut,
    ClientUpdate,
    ClientUserCreate,
    ClientUserOut,
    ClientUserUpdate,
)
from app.services import client_service

router = APIRouter()


@router.get("", response_model=list[ClientOut])
def list_clients(
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = None,
    _: AuthContext = Depends(require_permission("clients:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    return [client_out(client) for client in client_service.list_clients(db, status_filter, q)]


@router.post("", response_model=ClientOut, status_code=201)
def create_client(
    data: ClientCreate,
    context: AuthContext = Depends(require_permission("clients:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        client = client_service.create_client(db, context, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return client_out(client)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: str,
    _: AuthContext = Depends(require_permission("clients:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        client = client_service.get_client(db, client_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return client_out(client)


@router.patch("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: str,
    data: ClientUpdate,
    context: AuthContext = Depends(require_permission("clients:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        client = client_service.update_client(db, context, client_id, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return client_out(client)


@router.post("/{client_id}/suspend", response_model=ClientOut)
def suspend_client(
    client_id: str,
    context: AuthContext = Depends(require_permission("clients:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        client = client_service.set_client_status(db, context, client_id, "suspended")
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return client_out(client)


@router.post("/{client_id}/archive", response_model=ClientOut)
def archive_client(
    client_id: str,
    context: AuthContext = Depends(require_permission("clients:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        client = client_service.set_client_status(db, context, client_id, "archived")
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return client_out(client)


@router.get("/{client_id}/users", response_model=list[ClientUserOut])
def list_client_users(
    client_id: str,
    _: AuthContext = Depends(require_permission("clients:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    try:
        users = client_service.list_client_users(db, client_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return [client_user_out(user) for user in users]


@router.post("/{client_id}/users", response_model=ClientUserOut, status_code=201)
def create_client_user(
    client_id: str,
    data: ClientUserCreate,
    context: AuthContext = Depends(require_permission("clients:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = client_service.create_client_user(db, context, client_id, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return client_user_out(user)


@router.patch("/{client_id}/users/{user_id}", response_model=ClientUserOut)
def update_client_user(
    client_id: str,
    user_id: str,
    data: ClientUserUpdate,
    context: AuthContext = Depends(require_permission("clients:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = client_service.update_client_user(db, context, client_id, user_id, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return client_user_out(user)
