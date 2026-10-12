from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_ok():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_ok_and_no_secrets():
    response = client.get("/readyz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    names = {check["name"] for check in body["checks"]}
    assert {"config", "database", "agent"} <= names

    lowered = response.text.lower()
    for needle in ("password", "secret", "change-me", "sslmode", "db_host"):
        assert needle not in lowered


def test_openapi_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"]


def test_protected_endpoint_requires_auth():
    response = client.get("/api/v1/clients")
    assert response.status_code == 401
