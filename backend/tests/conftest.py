"""Fixtures compartidas: base de datos en memoria y clientes autenticados."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registra los modelos)
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.seed import seed
from app.db.session import get_db
from app.main import app
from app.models.user import HapmedUser, Role


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setenv("EVAS_SECRET_KEY", "test-secret")
    monkeypatch.setenv("EVAS_SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("EVAS_ENVIRONMENT", "test")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    session: Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    seed(session)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    def override():
        yield db_session

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_user(db_session: Session, email: str, password: str, roles: list[str]) -> HapmedUser:
    role_objects = list(db_session.scalars(select(Role).where(Role.code.in_(roles))).all())
    user = HapmedUser(
        email=email,
        full_name=email,
        password_hash=hash_password(password),
        is_active=True,
    )
    user.roles = role_objects
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def authenticate(client: TestClient, email: str, password: str) -> TestClient:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    csrf = client.cookies.get("evas_csrf")
    assert csrf
    client.headers.update({"X-CSRF-Token": csrf})
    return client


@pytest.fixture
def admin(db_session):
    return make_user(db_session, "admin@hapmed.test", "admin-password", ["superadmin"])


@pytest.fixture
def auth_client(client, admin):
    return authenticate(client, admin.email, "admin-password")
