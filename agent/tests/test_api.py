import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture
def client_with_token(monkeypatch):
    monkeypatch.setenv("EVAS_AGENT_TOKEN", "test-token")
    monkeypatch.setenv("EVAS_AGENT_MODE", "simulated")
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def test_healthz(client_with_token):
    response = client_with_token.get("/healthz")
    assert response.status_code == 200
    assert response.json()["mode"] == "simulated"


def test_operation_requires_token(client_with_token):
    response = client_with_token.post(
        "/v1/operations", json={"type": "health_check", "installation_id": "i1"}
    )
    assert response.status_code == 401


def test_operation_with_token_is_simulated(client_with_token):
    response = client_with_token.post(
        "/v1/operations",
        headers={"Authorization": "Bearer test-token"},
        json={
            "type": "upgrade_installation",
            "installation_id": "i1",
            "params": {"target_version": "1.5.0"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["simulated"] is True
    assert body["status"] == "accepted"


def test_operation_missing_param(client_with_token):
    response = client_with_token.post(
        "/v1/operations",
        headers={"Authorization": "Bearer test-token"},
        json={"type": "upgrade_installation", "installation_id": "i1", "params": {}},
    )
    assert response.status_code == 422


def test_operation_rejects_arbitrary_params(client_with_token):
    response = client_with_token.post(
        "/v1/operations",
        headers={"Authorization": "Bearer test-token"},
        json={
            "type": "restart_service",
            "installation_id": "i1",
            "params": {"service_name": "web", "image": "evil:latest"},
        },
    )
    assert response.status_code == 422


def test_fail_closed_without_token(monkeypatch):
    monkeypatch.delenv("EVAS_AGENT_TOKEN", raising=False)
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        response = test_client.post(
            "/v1/operations", json={"type": "health_check", "installation_id": "i1"}
        )
        assert response.status_code == 503
    get_settings.cache_clear()
