from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_ok_with_version():
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_readyz_ok():
    assert client.get("/readyz").status_code == 200
