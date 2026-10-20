"""Lógica de dominios y detección de conflictos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.core.config import get_settings
from app.models.infrastructure import Domain
from app.services import audit, cloudflare, installation_service
from app.services.util import as_uuid


def _normalize(fqdn: str) -> str:
    normalized = fqdn.strip().lower()
    if not normalized:
        raise ValueError("el dominio no es válido")
    return normalized


def is_available(db: Session, fqdn: str, exclude_domain_id=None) -> bool:
    stmt = select(Domain).where(Domain.fqdn == fqdn)
    if exclude_domain_id is not None:
        stmt = stmt.where(Domain.id != exclude_domain_id)
    return db.scalar(stmt) is None


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
    normalized = _normalize(fqdn)
    if not is_available(db, normalized):
        raise ValueError("el dominio ya está en uso")

    settings = get_settings()
    if settings.provision_enabled and installation.host_port:
        try:
            cloudflare.upsert_hostname(normalized, installation.host_port)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("no se pudo publicar el dominio en Cloudflare") from exc

    domain = Domain(installation_id=installation.id, fqdn=normalized, kind=kind)
    db.add(domain)
    db.flush()
    audit.record(db, context, "domain.create", "domain", domain.id, fqdn=normalized)
    db.commit()
    db.refresh(domain)
    return domain


def update_domain(db: Session, context: AuthContext, domain_id: str, fqdn: str) -> Domain:
    domain = get_domain(db, domain_id)
    normalized = _normalize(fqdn)
    if normalized == domain.fqdn:
        return domain
    if not is_available(db, normalized, domain.id):
        raise ValueError("el dominio ya está en uso")

    installation = installation_service.get_installation(db, str(domain.installation_id))
    settings = get_settings()
    old_fqdn = domain.fqdn
    published = False
    if settings.provision_enabled and installation.host_port:
        try:
            cloudflare.upsert_hostname(normalized, installation.host_port)
            published = True
        except Exception as exc:  # noqa: BLE001
            raise ValueError("no se pudo publicar el dominio en Cloudflare") from exc

    domain.fqdn = normalized
    audit.record(db, context, "domain.update", "domain", domain.id, old=old_fqdn, new=normalized)
    try:
        db.commit()
    except Exception:
        db.rollback()
        if published:
            try:
                cloudflare.delete_hostname(normalized)
            except Exception:  # noqa: BLE001
                pass
        raise

    db.refresh(domain)
    if published:
        try:
            cloudflare.delete_hostname(old_fqdn)
        except Exception:  # noqa: BLE001
            pass
    return domain


def delete_domain(db: Session, context: AuthContext, domain_id: str) -> None:
    domain = get_domain(db, domain_id)
    installation = installation_service.get_installation(db, str(domain.installation_id))
    settings = get_settings()
    if settings.provision_enabled and installation.host_port:
        try:
            cloudflare.delete_hostname(domain.fqdn)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("no se pudo eliminar el dominio en Cloudflare") from exc

    audit.record(db, context, "domain.delete", "domain", domain.id, fqdn=domain.fqdn)
    db.delete(domain)
    db.commit()
