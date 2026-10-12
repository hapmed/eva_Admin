from app.services.webauthn_service import ADJECTIVES, ANIMALS, generate_name


def test_generate_name_format_and_unique(db_session, admin):
    names = set()
    for _ in range(10):
        name = generate_name(db_session, admin.id)
        parts = name.split(" ")
        assert parts[0] in ADJECTIVES
        assert parts[1] in ANIMALS
        names.add(name)
    assert len(names) == 10


def test_register_begin_requires_auth(client):
    assert client.post("/api/v1/auth/webauthn/register/begin").status_code == 401


def test_register_begin_returns_options(auth_client):
    response = auth_client.post("/api/v1/auth/webauthn/register/begin")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["challenge"]
    assert body["rp"]["id"]


def test_credentials_list_empty(auth_client):
    response = auth_client.get("/api/v1/auth/webauthn/credentials")
    assert response.status_code == 200
    assert response.json() == []


def test_login_begin_returns_options(client):
    response = client.post("/api/v1/auth/webauthn/login/begin", json={})
    assert response.status_code == 200
    assert response.json()["challenge"]


def test_me_reports_passkey_state(auth_client):
    body = auth_client.get("/api/v1/auth/me").json()
    assert body["has_passkeys"] is False
    assert body["passkey_name"] is None
