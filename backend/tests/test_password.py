def test_password_change_flow(auth_client, admin):
    change = auth_client.post(
        "/api/v1/auth/password/change",
        json={"current_password": "admin-password", "new_password": "nueva-password-123"},
    )
    assert change.status_code == 200

    auth_client.post("/api/v1/auth/logout")
    login = auth_client.post(
        "/api/v1/auth/login",
        json={"email": admin.email, "password": "nueva-password-123"},
    )
    assert login.status_code == 200


def test_password_change_wrong_current(auth_client):
    response = auth_client.post(
        "/api/v1/auth/password/change",
        json={"current_password": "incorrecta", "new_password": "otra-password-123"},
    )
    assert response.status_code == 400
