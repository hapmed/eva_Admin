def test_system_requires_auth(client):
    assert client.get("/api/v1/system").status_code == 401


def test_system_returns_stats(auth_client):
    response = auth_client.get("/api/v1/system")
    assert response.status_code == 200
    body = response.json()
    assert "cpu_percent" in body
    assert "mem_percent" in body
    assert "disk_percent" in body
    assert body["simulated"] is True  # agente simulado en tests
