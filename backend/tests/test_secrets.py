import uuid

from sqlalchemy import select

from app.models.eva import EvaProduct
from app.models.infrastructure import Installation, InstallationSecret, SecretReference
from app.services import secrets_service
from app.services.installation_service import _deploy_spec


def _declare(db_session, installation_id, key: str) -> None:
    db_session.add(SecretReference(installation_id=installation_id, key=key, provider="env", path=""))
    db_session.flush()


def test_secret_value_is_stable_and_encrypted(db_session):
    installation_id = uuid.uuid4()
    first = secrets_service.get_or_create_value(db_session, installation_id, "JWT_SECRET")
    second = secrets_service.get_or_create_value(db_session, installation_id, "JWT_SECRET")

    assert first == second
    assert len(first) >= 20
    row = db_session.scalar(select(InstallationSecret).where(InstallationSecret.key == "JWT_SECRET"))
    assert row is not None
    assert first not in row.value_encrypted


def test_env_for_injects_declared_secrets(db_session):
    installation_id = uuid.uuid4()
    _declare(db_session, installation_id, "JWT_SECRET")
    _declare(db_session, installation_id, "SIGNING_KEY")

    env = secrets_service.env_for(db_session, installation_id)

    assert set(env) == {"JWT_SECRET", "SIGNING_KEY"}
    assert all(len(value) >= 20 for value in env.values())


def test_deploy_spec_includes_migrate_command():
    eva = EvaProduct(
        code="demo",
        name="Demo",
        container_port=8000,
        migrate_command="alembic upgrade head",
    )
    installation = Installation(
        client_id=uuid.uuid4(),
        eva_product_id=uuid.uuid4(),
        host_port=9100,
        container_name="eva_demo",
    )

    spec = _deploy_spec(eva, installation, "1.0.0", {}, {})

    assert spec["migrate"] == "alembic upgrade head"


def test_deploy_spec_omits_migrate_when_empty():
    eva = EvaProduct(code="demo", name="Demo", container_port=8000)
    installation = Installation(
        client_id=uuid.uuid4(),
        eva_product_id=uuid.uuid4(),
        host_port=9100,
        container_name="eva_demo",
    )

    spec = _deploy_spec(eva, installation, "1.0.0", {}, {})

    assert "migrate" not in spec
