from tests.factories import make_client, make_eva, make_installation


class FailingAgent:
    """Agente que siempre falla (simula un fallo del canal backend⇄agente)."""

    mode = "real"

    def upgrade_installation(self, *args, **kwargs):
        raise RuntimeError("fallo simulado del agente")


def test_agent_failure_marks_operation_failed(monkeypatch, auth_client):
    client = make_client(auth_client, "FailOp")
    eva = make_eva(auth_client, code="failop", version="1.0.0")
    auth_client.post(f"/api/v1/evas/{eva['id']}/versions", json={"version": "1.1.0"})
    installation = make_installation(auth_client, client["id"], eva["id"]).json()

    monkeypatch.setattr("app.services.operations.get_agent", lambda: FailingAgent())

    response = auth_client.post(
        f"/api/v1/installations/{installation['id']}/upgrade",
        json={"target_version": "1.1.0"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["error_code"] == "agent_error"
