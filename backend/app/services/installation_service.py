"""Lógica de instalaciones (aprovisionamiento real: BD + contenedor + DNS)."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthContext
from app.core.config import get_settings
from app.models.eva import EvaProduct, EvaVersion
from app.models.infrastructure import (
    DatabaseRecord,
    Domain,
    Installation,
    InstallationConfig,
    InstallationService,
    Node,
    SecretReference,
)
from app.models.monitoring import Backup
from app.schemas.installation import InstallationCreate, InstallationUpdate
from app.services import (
    audit,
    client_service,
    cloudflare,
    config_schema,
    eva_service,
    monitoring_service,
    operations,
    provisioning,
    subscription_service,
)
from app.services.util import as_uuid


def _resolve_node(db: Session, node_id: str | None) -> Node | None:
    if node_id:
        node = db.get(Node, as_uuid(node_id))
        if node is None:
            raise LookupError("nodo no encontrado")
        return node
    return db.scalar(select(Node).order_by(Node.created_at))


def _approved_version(db: Session, eva: EvaProduct, version: str) -> EvaVersion:
    found = db.scalar(
        select(EvaVersion).where(EvaVersion.eva_product_id == eva.id, EvaVersion.version == version)
    )
    if found is None:
        raise ValueError("la versión no está registrada para esta EVA")
    if found.status != "approved":
        raise ValueError("la versión no está aprobada")
    return found


def _image(eva: EvaProduct, version: str) -> str:
    repo = eva.image_repo or f"eva-{eva.code}"
    return f"{repo}:{version}"


def _service_env(
    eva: EvaProduct,
    installation: Installation,
    client_ref: str,
    version: str,
    config: dict,
    database_url: str | None,
) -> dict[str, str]:
    env: dict[str, str] = {
        "EVAS_EVA_CODE": eva.code,
        "EVAS_INSTALLATION_ID": str(installation.id),
        "EVAS_CLIENT_REF": client_ref,
        "EVAS_VERSION": version,
        "PORT": str(eva.container_port),
    }
    if database_url:
        env["DATABASE_URL"] = database_url
    for key, value in config.items():
        env[key.upper()] = str(value)
    return env


def _service_labels(
    eva: EvaProduct, installation: Installation, client_ref: str, version: str
) -> dict[str, str]:
    return {
        "evas.managed_by": "evas-admin",
        "evas.installation_id": str(installation.id),
        "evas.eva_code": eva.code,
        "evas.client_ref": client_ref,
        "evas.version": version,
        "evas.service": eva.code,
    }


def _deploy_spec(eva: EvaProduct, installation: Installation, version: str, env: dict, labels: dict) -> dict:
    settings = get_settings()
    return {
        "installation_id": str(installation.id),
        "image": _image(eva, version),
        "name": installation.container_name,
        "network": settings.eva_network,
        "host_port": installation.host_port,
        "container_port": eva.container_port,
        "env": env,
        "labels": labels,
    }


def list_secrets(db: Session, installation_id: str) -> list[SecretReference]:
    return list(
        db.scalars(
            select(SecretReference)
            .where(SecretReference.installation_id == as_uuid(installation_id))
            .order_by(SecretReference.key)
        ).all()
    )


def list_installations(
    db: Session, client_id: str | None = None, status: str | None = None
) -> list[Installation]:
    stmt = select(Installation).order_by(Installation.created_at)
    if client_id:
        stmt = stmt.where(Installation.client_id == as_uuid(client_id))
    if status:
        stmt = stmt.where(Installation.status == status)
    return list(db.scalars(stmt).all())


def get_installation(db: Session, installation_id: str) -> Installation:
    installation = db.get(Installation, as_uuid(installation_id))
    if installation is None:
        raise LookupError("instalación no encontrada")
    return installation


def create_installation(db: Session, context: AuthContext, data: InstallationCreate) -> Installation:
    settings = get_settings()
    client = client_service.get_client(db, data.client_id)
    eva = eva_service.get_eva(db, data.eva_product_id)
    node = _resolve_node(db, data.node_id)

    if data.subscription_id:
        subscription = subscription_service.get_subscription(db, data.subscription_id)
        if str(subscription.client_id) != str(client.id):
            raise ValueError("la suscripción no pertenece al cliente")

    config_schema.validate_config(eva.config_schema, data.config)
    _approved_version(db, eva, data.desired_version)

    if data.primary_domain and db.scalar(select(Domain).where(Domain.fqdn == data.primary_domain)):
        raise ValueError("el dominio ya está en uso")

    installation = Installation(
        client_id=client.id,
        eva_product_id=eva.id,
        subscription_id=as_uuid(data.subscription_id) if data.subscription_id else None,
        node_id=node.id if node else None,
        environment=data.environment,
        status="pending",
        desired_version=data.desired_version,
        host_port=provisioning.allocate_port(db),
        container_name=provisioning.container_name(str(client.id), eva.code),
    )
    db.add(installation)
    db.flush()

    database_url: str | None = None
    if settings.provision_enabled:
        db_name, _db_user, database_url = provisioning.provision_database(str(client.id), eva.code)
        db.add(
            DatabaseRecord(
                installation_id=installation.id,
                engine="postgresql",
                logical_name=db_name,
                host_ref=node.host_ref if node else "",
                status="active",
            )
        )

    db.add(InstallationConfig(installation_id=installation.id, config_json=data.config))
    db.add(
        InstallationService(
            installation_id=installation.id,
            service_name=eva.code,
            container_ref=installation.container_name,
            image_ref=_image(eva, data.desired_version),
        )
    )
    for reference in data.secrets:
        db.add(
            SecretReference(
                installation_id=installation.id,
                key=reference.key,
                provider=reference.provider,
                path=reference.path,
            )
        )
    if data.primary_domain:
        db.add(
            Domain(
                installation_id=installation.id,
                fqdn=data.primary_domain,
                kind="primary",
                status="active",
            )
        )

    env = _service_env(eva, installation, str(client.id), data.desired_version, data.config, database_url)
    labels = _service_labels(eva, installation, str(client.id), data.desired_version)
    spec = _deploy_spec(eva, installation, data.desired_version, env, labels)

    operations.run(
        db,
        context,
        str(installation.id),
        "deploy_installation",
        idempotency_key=data.idempotency_key,
        call=lambda agent: agent.deploy_installation(spec),
        summary="despliegue inicial",
    )

    if settings.provision_enabled and data.primary_domain and installation.host_port:
        try:
            cloudflare.upsert_hostname(data.primary_domain, installation.host_port)
        except Exception:  # noqa: BLE001 - no bloquear el alta por DNS
            pass

    installation.status = "active"
    installation.installed_version = data.desired_version
    installation.last_operation_at = datetime.now(UTC)
    db.commit()
    db.refresh(installation)
    return installation


def update_installation(
    db: Session, context: AuthContext, installation_id: str, data: InstallationUpdate
) -> Installation:
    installation = get_installation(db, installation_id)
    if data.environment is not None:
        installation.environment = data.environment
    if data.desired_version is not None:
        installation.desired_version = data.desired_version
    audit.record(db, context, "installation.update", "installation", installation.id)
    db.commit()
    db.refresh(installation)
    return installation


def upgrade(
    db: Session,
    context: AuthContext,
    installation_id: str,
    target_version: str,
    idempotency_key: str | None = None,
) -> tuple[Installation, object]:
    settings = get_settings()
    installation = get_installation(db, installation_id)
    eva = db.get(EvaProduct, installation.eva_product_id)
    if eva is None:
        raise LookupError("EVA no encontrada")
    _approved_version(db, eva, target_version)

    config_row = db.scalar(
        select(InstallationConfig).where(InstallationConfig.installation_id == installation.id)
    )
    config = config_row.config_json if config_row else {}

    database_url: str | None = None
    if settings.provision_enabled:
        _db_name, _db_user, database_url = provisioning.provision_database(
            str(installation.client_id), eva.code
        )

    version = target_version
    env = _service_env(eva, installation, str(installation.client_id), version, config, database_url)
    labels = _service_labels(eva, installation, str(installation.client_id), version)
    spec = _deploy_spec(eva, installation, version, env, labels)

    operation = operations.run(
        db,
        context,
        str(installation.id),
        "upgrade_installation",
        idempotency_key=idempotency_key,
        call=lambda agent: agent.upgrade_installation(spec),
        summary=f"actualización a {target_version}",
    )
    installation.desired_version = target_version
    installation.installed_version = target_version
    installation.status = "active"
    installation.last_operation_at = datetime.now(UTC)

    now = datetime.now(UTC)
    databases = db.scalars(
        select(DatabaseRecord).where(DatabaseRecord.installation_id == installation.id)
    ).all()
    for record in databases:
        db.add(
            Backup(
                database_record_id=record.id,
                type="full",
                status="simulated",
                started_at=now,
                finished_at=now,
            )
        )

    db.commit()
    db.refresh(installation)
    return installation, operation


def restart(
    db: Session,
    context: AuthContext,
    installation_id: str,
    service_name: str,
    idempotency_key: str | None = None,
):
    installation = get_installation(db, installation_id)
    operation = operations.run(
        db,
        context,
        str(installation.id),
        "restart_service",
        idempotency_key=idempotency_key,
        call=lambda agent: agent.restart_service(str(installation.id), service_name),
        summary=f"reinicio de {service_name}",
    )
    installation.last_operation_at = datetime.now(UTC)
    db.commit()
    return operation


def health_check(db: Session, context: AuthContext, installation_id: str):
    installation = get_installation(db, installation_id)
    op = operations.run(
        db,
        context,
        str(installation.id),
        "health_check",
        call=lambda agent: agent.health_check(str(installation.id)),
        summary="comprobación de salud",
    )
    monitoring_service.record_health_check(db, installation)
    installation.last_operation_at = datetime.now(UTC)
    db.commit()
    return op
