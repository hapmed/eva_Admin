"""Lógica de dominios y detección de conflictos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.models.infrastructure import Domain
from app.services import audit, installation_service
from app.services.util import as_uuid


def is_available(db: Session, fqdn: str) -> bool:
    return db.scalar(select(Domain).where(Domain.fqdn == fqdn)) is None


def list_domains(db: Session, installation_id: str | None = None) -> list[Domain]:
    stmt = select(Domain).order_by(Domain.fqdn)
    if installation_id:
        stmt = stmt.where(Domain.installation_id == as_uuid(installation_id))
    return list(db.scalars(stmt).all())


def get_domain(db: Session, domain_id: str) -> Domain:
    domain = db.get(Domain, as_uuid(domain_id))
    if domain is None:
        raise LookupError("dominio no encontrado")
    return domain


def create_domain(db: Session, context: AuthContext, installation_id: str, fqdn: str, kind: str) -> Domain:
    installation = installation_service.get_installation(db, installation_id)
    normalized = fqdn.strip().lower()
    if not is_available(db, normalized):
        raise ValueError("el dominio ya está en uso")
    domain = Domain(installation_id=installation.id, fqdn=normalized, kind=kind)
    db.add(domain)
    db.flush()
    audit.record(db, context, "domain.create", "domain", domain.id, fqdn=normalized)
    db.commit()
    db.refresh(domain)
    return domain


def delete_domain(db: Session, context: AuthContext, domain_id: str) -> None:
    domain = get_domain(db, domain_id)
    audit.record(db, context, "domain.delete", "domain", domain.id, fqdn=domain.fqdn)
    db.delete(domain)
    db.commit()
