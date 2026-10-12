from app.core.security import hash_token
from app.models.token import ApiToken
from tests.conftest import authenticate, make_user


def test_login_and_me(auth_client):
    response = auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@hapmed.test"
    assert "users:read" in body["permissions"]
    assert "superadmin" in body["roles"]


def test_login_wrong_password(client, admin):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin.email, "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_cookie_mutation_requires_csrf(client, admin):
    login = client.post("/api/v1/auth/login", json={"email": admin.email, "password": "admin-password"})
    assert login.status_code == 200
    # Sin cabecera CSRF -> 403
    response = client.post("/api/v1/clients", json={"legal_name": "A", "display_name": "A"})
    assert response.status_code == 403


def test_bearer_token_scopes(client, db_session):
    db_session.add(
        ApiToken(
            name="integration",
            owner_type="integration",
            scopes=["clients:read"],
            token_hash=hash_token("secret-token"),
            status="active",
        )
    )
    db_session.commit()

    headers = {"Authorization": "Bearer secret-token"}
    assert client.get("/api/v1/clients", headers=headers).status_code == 200
    # sin el scope clients:write -> 403
    response = client.post(
        "/api/v1/clients",
        headers=headers,
        json={"legal_name": "A", "display_name": "A"},
    )
    assert response.status_code == 403


def test_read_only_cannot_write(db_session, client):
    make_user(db_session, "viewer@hapmed.test", "viewer-password", ["read_only"])
    authenticate(client, "viewer@hapmed.test", "viewer-password")
    assert client.get("/api/v1/clients").status_code == 200
    response = client.post("/api/v1/clients", json={"legal_name": "A", "display_name": "A"})
    assert response.status_code == 403


def test_logout_clears_session(auth_client):
    assert auth_client.post("/api/v1/auth/logout").status_code == 200
    # Tras logout sin cookies válidas -> 401
    assert auth_client.get("/api/v1/clients").status_code == 401
