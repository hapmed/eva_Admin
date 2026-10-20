def _create_client(auth_client, name: str) -> dict:
    response = auth_client.post(
        "/api/v1/clients", json={"legal_name": f"Cliente {name}", "display_name": name}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_client_crud(auth_client):
    client = _create_client(auth_client, "Alfa")
    assert client["status"] == "active"

    updated = auth_client.patch(
        f"/api/v1/clients/{client['id']}",
        json={"display_name": "Alfa S.L.", "tax_id": "ABC010101XYZ", "notes": "Cliente piloto"},
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Alfa S.L."
    assert updated.json()["tax_id"] == "ABC010101XYZ"
    assert updated.json()["notes"] == "Cliente piloto"

    listing = auth_client.get("/api/v1/clients")
    assert any(item["id"] == client["id"] for item in listing.json())


def test_client_slug_is_derived_from_rfc_and_unique(auth_client):
    first = auth_client.post(
        "/api/v1/clients",
        json={"legal_name": "Alfa SA", "display_name": "Alfa", "tax_id": "ABC010101XYZ"},
    )
    second = auth_client.post(
        "/api/v1/clients",
        json={"legal_name": "Beta SA", "display_name": "Beta", "tax_id": "ABC010101XYZ"},
    )
    assert first.status_code == 201 and second.status_code == 201
    assert first.json()["slug"] == "abc"
    assert second.json()["slug"] == "abc2"
    assert first.json()["suggested_domain"] == "abc.hapmed.qzz.io"
    assert second.json()["suggested_domain"] == "abc2.hapmed.qzz.io"

    updated = auth_client.patch(f"/api/v1/clients/{second.json()['id']}", json={"slug": "beta"})
    assert updated.status_code == 200
    assert updated.json()["slug"] == "beta"


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
