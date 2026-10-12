"""Catálogo de aplicaciones EVA."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import eva_out, eva_version_out
from app.db.session import get_db
from app.schemas.eva import EvaCreate, EvaOut, EvaUpdate, EvaVersionCreate, EvaVersionOut
from app.services import eva_service

router = APIRouter()


@router.get("", response_model=list[EvaOut])
def list_evas(
    _: AuthContext = Depends(require_permission("evas:read")), db: Session = Depends(get_db)
) -> list[dict]:
    return [eva_out(eva) for eva in eva_service.list_evas(db)]


@router.post("", response_model=EvaOut, status_code=201)
def create_eva(
    data: EvaCreate,
    context: AuthContext = Depends(require_permission("evas:manage")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        eva = eva_service.create_eva(db, context, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return eva_out(eva)


@router.get("/{eva_id}", response_model=EvaOut)
def get_eva(
    eva_id: str,
    _: AuthContext = Depends(require_permission("evas:read")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        eva = eva_service.get_eva(db, eva_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return eva_out(eva)


@router.patch("/{eva_id}", response_model=EvaOut)
def update_eva(
    eva_id: str,
    data: EvaUpdate,
    context: AuthContext = Depends(require_permission("evas:manage")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        eva = eva_service.update_eva(db, context, eva_id, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return eva_out(eva)


@router.get("/{eva_id}/versions", response_model=list[EvaVersionOut])
def list_versions(
    eva_id: str,
    _: AuthContext = Depends(require_permission("evas:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    try:
        versions = eva_service.list_versions(db, eva_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return [eva_version_out(version) for version in versions]


@router.post("/{eva_id}/versions", response_model=EvaVersionOut, status_code=201)
def add_version(
    eva_id: str,
    data: EvaVersionCreate,
    context: AuthContext = Depends(require_permission("evas:manage")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        version = eva_service.add_version(db, context, eva_id, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return eva_version_out(version)
