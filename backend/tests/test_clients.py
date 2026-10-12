def _create_client(auth_client, name: str) -> dict:
    response = auth_client.post(
        "/api/v1/clients", json={"legal_name": f"Cliente {name}", "display_name": name}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_client_crud(auth_client):
    client = _create_client(auth_client, "Alfa")
    assert client["status"] == "active"

    updated = auth_client.patch(f"/api/v1/clients/{client['id']}", json={"display_name": "Alfa S.L."})
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Alfa S.L."

    listing = auth_client.get("/api/v1/clients")
    assert any(item["id"] == client["id"] for item in listing.json())


def test_suspend_and_archive(auth_client):
    client = _create_client(auth_client, "Beta")
    assert auth_client.post(f"/api/v1/clients/{client['id']}/suspend").json()["status"] == "suspended"
    assert auth_client.post(f"/api/v1/clients/{client['id']}/archive").json()["status"] == "archived"


def test_client_users_are_isolated_per_client(auth_client):
    client_a = _create_client(auth_client, "Alfa")
    client_b = _create_client(auth_client, "Beta")

    assert (
        auth_client.post(
            f"/api/v1/clients/{client_a['id']}/users",
            json={"email": "ua@alfa.test", "password": "password-a"},
        ).status_code
        == 201
    )
    assert (
        auth_client.post(
            f"/api/v1/clients/{client_b['id']}/users",
            json={"email": "ub@beta.test", "password": "password-b"},
        ).status_code
        == 201
    )

    users_a = auth_client.get(f"/api/v1/clients/{client_a['id']}/users").json()
    users_b = auth_client.get(f"/api/v1/clients/{client_b['id']}/users").json()
    assert [user["email"] for user in users_a] == ["ua@alfa.test"]
    assert [user["email"] for user in users_b] == ["ub@beta.test"]
