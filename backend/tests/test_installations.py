from tests.conftest import authenticate, make_user
from tests.factories import make_client, make_eva, make_installation


def test_create_installation_with_config_domain_and_secrets(auth_client):
    client = make_client(auth_client, "Alfa")
    eva = make_eva(
        auth_client,
        code="cotizaciones",
        config_schema={"properties": {"port": {"type": "integer"}}, "required": ["port"]},
    )
    response = make_installation(
        auth_client,
        client["id"],
        eva["id"],
        config={"port": 8000},
        primary_domain="alfa.ejemplo.test",
        secrets=[{"key": "DB_PASSWORD", "provider": "env", "path": "secret/db"}],
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "active"
    assert body["installed_version"] == "1.0.0"
    assert body["domains"] == ["alfa.ejemplo.test"]
    assert body["secrets"] == [{"key": "DB_PASSWORD", "provider": "env"}]
    assert "secret/db" not in response.text


def test_config_rejected_when_invalid(auth_client):
    client = make_client(auth_client, "Beta")
    eva = make_eva(
        auth_client,
        code="cfg",
        config_schema={"properties": {"port": {"type": "integer"}}, "required": ["port"]},
    )
    assert make_installation(auth_client, client["id"], eva["id"], config={"port": "x"}).status_code == 409
    assert make_installation(auth_client, client["id"], eva["id"], config={"nope": 1}).status_code == 409
    assert make_installation(auth_client, client["id"], eva["id"], config={}).status_code == 409


def test_unapproved_version_rejected(auth_client):
    client = make_client(auth_client, "Gamma")
    eva = make_eva(auth_client, code="unapp", version="2.0.0", version_status="deprecated")
    response = make_installation(auth_client, client["id"], eva["id"], desired_version="2.0.0")
    assert response.status_code == 409


def test_domain_conflict_on_installations(auth_client):
    client_a = make_client(auth_client, "DomA")
    client_b = make_client(auth_client, "DomB")
    eva = make_eva(auth_client, code="dom-clash")
    assert (
        make_installation(auth_client, client_a["id"], eva["id"], primary_domain="dup.test").status_code
        == 201
    )
    assert (
        make_installation(auth_client, client_b["id"], eva["id"], primary_domain="dup.test").status_code
        == 409
    )


def test_upgrade_and_idempotency(auth_client):
    client = make_client(auth_client, "Up")
    eva = make_eva(auth_client, code="up", version="1.0.0")
    auth_client.post(f"/api/v1/evas/{eva['id']}/versions", json={"version": "1.1.0"})
    installation = make_installation(auth_client, client["id"], eva["id"]).json()

    first = auth_client.post(
        f"/api/v1/installations/{installation['id']}/upgrade",
        json={"target_version": "1.1.0", "idempotency_key": "k1"},
    )
    assert first.status_code == 200 and first.json()["simulated"] is True

    second = auth_client.post(
        f"/api/v1/installations/{installation['id']}/upgrade",
        json={"target_version": "1.1.0", "idempotency_key": "k1"},
    )
    assert second.json()["id"] == first.json()["id"]

    operations = auth_client.get(f"/api/v1/operations?installation_id={installation['id']}").json()
    assert sum(1 for op in operations if op["type"] == "upgrade_installation") == 1

    detail = auth_client.get(f"/api/v1/installations/{installation['id']}").json()
    assert detail["installed_version"] == "1.1.0"


def test_delete_installation_removes_resources_and_keeps_client(auth_client):
    client = make_client(auth_client, "Delete")
    eva = make_eva(auth_client, code="del")
    installation = make_installation(
        auth_client, client["id"], eva["id"], primary_domain="del.ejemplo.test"
    ).json()

    response = auth_client.delete(f"/api/v1/installations/{installation['id']}")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["deleted"] is True
    assert body["warnings"] == []
    assert auth_client.get(f"/api/v1/installations/{installation['id']}").status_code == 404
    assert auth_client.get(f"/api/v1/installations?client_id={client['id']}").json() == []

    clients = auth_client.get("/api/v1/clients").json()
    assert any(item["id"] == client["id"] for item in clients)


def test_installation_access_can_be_created_and_reset(auth_client, monkeypatch):
    client = make_client(auth_client, "Acceso")
    eva = make_eva(auth_client, code="acceso")
    installation = make_installation(
        auth_client, client["id"], eva["id"], primary_domain="acceso.ejemplo.test"
    ).json()

    initial = auth_client.get(f"/api/v1/installations/{installation['id']}/access")
    assert initial.status_code == 200
    assert initial.json() == {"email": None, "password": None}

    monkeypatch.setattr("app.services.eva_users.create_user", lambda *args, **kwargs: {"id": "1"})
    created = auth_client.post(f"/api/v1/installations/{installation['id']}/access")
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["email"] == "admin@acceso.ejemplo.test"
    assert body["password"]

    current = auth_client.get(f"/api/v1/installations/{installation['id']}/access")
    assert current.json() == body

    monkeypatch.setattr("app.services.eva_users.reset_password_by_email", lambda *args, **kwargs: None)
    reset = auth_client.post(f"/api/v1/installations/{installation['id']}/access/reset")
    assert reset.status_code == 200, reset.text
    assert reset.json()["email"] == body["email"]
    assert reset.json()["password"] != body["password"]


def test_delete_installation_requires_permission(db_session, client):
    make_user(db_session, "viewer5@hapmed.test", "viewer-password", ["read_only"])
    authenticate(client, "viewer5@hapmed.test", "viewer-password")
    response = client.delete("/api/v1/installations/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 403


def test_installation_isolation_by_client(auth_client):
    client_a = make_client(auth_client, "IsoA")
    client_b = make_client(auth_client, "IsoB")
    eva = make_eva(auth_client, code="iso")
    make_installation(auth_client, client_a["id"], eva["id"])
    make_installation(auth_client, client_b["id"], eva["id"])

    only_a = auth_client.get(f"/api/v1/installations?client_id={client_a['id']}").json()
    assert len(only_a) == 1
    assert only_a[0]["client_id"] == client_a["id"]


def test_create_installation_requires_permission(db_session, client):
    make_user(db_session, "viewer4@hapmed.test", "viewer-password", ["read_only"])
    authenticate(client, "viewer4@hapmed.test", "viewer-password")
    response = client.post(
        "/api/v1/installations",
        json={"client_id": "x", "eva_product_id": "y", "desired_version": "1.0.0"},
    )
    assert response.status_code == 403
