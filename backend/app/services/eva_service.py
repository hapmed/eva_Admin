"""Lógica del catálogo EVA."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.models.eva import EvaProduct, EvaVersion
from app.schemas.eva import EvaCreate, EvaUpdate, EvaVersionCreate
from app.services import audit
from app.services.util import as_uuid


def list_evas(db: Session) -> list[EvaProduct]:
    return list(db.scalars(select(EvaProduct).order_by(EvaProduct.code)).all())


def get_eva(db: Session, eva_id: str) -> EvaProduct:
    eva = db.get(EvaProduct, as_uuid(eva_id))
    if eva is None:
        raise LookupError("EVA no encontrada")
    return eva


def create_eva(db: Session, context: AuthContext, data: EvaCreate) -> EvaProduct:
    if db.scalar(select(EvaProduct).where(EvaProduct.code == data.code)):
        raise ValueError("el código de EVA ya existe")
    eva = EvaProduct(
        code=data.code,
        name=data.name,
        description=data.description,
        config_schema=data.config_schema,
    )
    db.add(eva)
    db.flush()
    audit.record(db, context, "eva.create", "eva_product", eva.id, code=eva.code)
    db.commit()
    db.refresh(eva)
    return eva


def update_eva(db: Session, context: AuthContext, eva_id: str, data: EvaUpdate) -> EvaProduct:
    eva = get_eva(db, eva_id)
    for field in ("name", "description", "status", "config_schema"):
        value = getattr(data, field)
        if value is not None:
            setattr(eva, field, value)
    audit.record(db, context, "eva.update", "eva_product", eva.id)
    db.commit()
    db.refresh(eva)
    return eva


def list_versions(db: Session, eva_id: str) -> list[EvaVersion]:
    eva = get_eva(db, eva_id)
    return list(
        db.scalars(
            select(EvaVersion).where(EvaVersion.eva_product_id == eva.id).order_by(EvaVersion.created_at)
        ).all()
    )


def add_version(db: Session, context: AuthContext, eva_id: str, data: EvaVersionCreate) -> EvaVersion:
    eva = get_eva(db, eva_id)
    exists = db.scalar(
        select(EvaVersion).where(EvaVersion.eva_product_id == eva.id, EvaVersion.version == data.version)
    )
    if exists:
        raise ValueError("la versión ya existe para esta EVA")
    version = EvaVersion(
        eva_product_id=eva.id,
        version=data.version,
        status=data.status,
        deployment_requirements=data.deployment_requirements,
    )
    db.add(version)
    db.flush()
    audit.record(db, context, "eva.add_version", "eva_version", version.id, version=version.version)
    db.commit()
    db.refresh(version)
    return version
