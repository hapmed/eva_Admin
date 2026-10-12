def test_create_and_list_users(auth_client):
    response = auth_client.post(
        "/api/v1/users",
        json={
            "email": "op@hapmed.test",
            "password": "op-password",
            "roles": ["operations"],
            "full_name": "Operaciones",
        },
    )
    assert response.status_code == 201, response.text
    assert "operations" in response.json()["roles"]

    listing = auth_client.get("/api/v1/users")
    assert listing.status_code == 200
    assert any(user["email"] == "op@hapmed.test" for user in listing.json())


def test_duplicate_email_conflict(auth_client, admin):
    response = auth_client.post(
        "/api/v1/users",
        json={"email": admin.email, "password": "another-password", "roles": []},
    )
    assert response.status_code == 409


def test_unknown_role_is_rejected(auth_client):
    response = auth_client.post(
        "/api/v1/users",
        json={"email": "nope@hapmed.test", "password": "nope-password", "roles": ["ghost"]},
    )
    assert response.status_code == 409


def test_cannot_change_own_roles(auth_client):
    me = auth_client.get("/api/v1/auth/me").json()
    response = auth_client.put(f"/api/v1/users/{me['id']}/roles", json={"roles": ["read_only"]})
    assert response.status_code == 409


def test_deactivate_and_self_deactivation_forbidden(auth_client):
    created = auth_client.post(
        "/api/v1/users",
        json={"email": "temp@hapmed.test", "password": "temp-password", "roles": ["read_only"]},
    ).json()
    deactivated = auth_client.post(f"/api/v1/users/{created['id']}/deactivate")
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    me = auth_client.get("/api/v1/auth/me").json()
    assert auth_client.post(f"/api/v1/users/{me['id']}/deactivate").status_code == 409


def test_roles_and_permissions_catalog(auth_client):
    roles = auth_client.get("/api/v1/roles").json()
    assert {"superadmin", "operations", "customer_care", "read_only"} <= {role["code"] for role in roles}
    permissions = auth_client.get("/api/v1/permissions").json()
    assert any(permission["code"] == "clients:write" for permission in permissions)
