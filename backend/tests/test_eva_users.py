from app.services.eva_users import hash_password


def test_hash_password_is_bcrypt():
    stored = hash_password("s3cret-password")
    assert stored.startswith("$2")
    assert "s3cret-password" not in stored


def test_list_eva_users_requires_auth(client):
    response = client.get("/api/v1/installations/00000000-0000-0000-0000-000000000000/users")
    assert response.status_code == 401
