def test_public_config(client):
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    body = response.json()
    assert "client_name" in body
    assert "version" in body
