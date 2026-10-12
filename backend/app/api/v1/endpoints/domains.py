"""Dominios y comprobación de conflictos."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import domain_out
from app.db.session import get_db
from app.schemas.installation import DomainCheck, DomainCreate, DomainOut
from app.services import domain_service

router = APIRouter()


@router.get("", response_model=list[DomainOut])
def list_domains(
    installation_id: str | None = None,
    _: AuthContext = Depends(require_permission("domains:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    return [domain_out(domain) for domain in domain_service.list_domains(db, installation_id)]


@router.get("/check", response_model=DomainCheck)
def check_domain(
    fqdn: str,
    _: AuthContext = Depends(require_permission("domains:read")),
    db: Session = Depends(get_db),
) -> DomainCheck:
    normalized = fqdn.strip().lower()
    return DomainCheck(fqdn=normalized, available=domain_service.is_available(db, normalized))


@router.post("", response_model=DomainOut, status_code=201)
def create_domain(
    data: DomainCreate,
    context: AuthContext = Depends(require_permission("domains:write")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        domain = domain_service.create_domain(db, context, data.installation_id, data.fqdn, data.kind)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return domain_out(domain)


@router.delete("/{domain_id}", status_code=204)
def delete_domain(
    domain_id: str,
    context: AuthContext = Depends(require_permission("domains:write")),
    db: Session = Depends(get_db),
) -> None:
    try:
        domain_service.delete_domain(db, context, domain_id)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
