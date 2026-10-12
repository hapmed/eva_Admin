from tests.factories import make_client, make_eva, make_installation


def test_domain_endpoints_and_conflict(auth_client):
    client = make_client(auth_client, "Dom")
    eva = make_eva(auth_client, code="domx")
    installation = make_installation(auth_client, client["id"], eva["id"]).json()

    created = auth_client.post(
        "/api/v1/domains", json={"installation_id": installation["id"], "fqdn": "App.Dom.Test"}
    )
    assert created.status_code == 201, created.text
    assert created.json()["fqdn"] == "app.dom.test"

    duplicate = auth_client.post(
        "/api/v1/domains", json={"installation_id": installation["id"], "fqdn": "app.dom.test"}
    )
    assert duplicate.status_code == 409

    assert auth_client.get("/api/v1/domains/check?fqdn=app.dom.test").json()["available"] is False
    assert auth_client.get("/api/v1/domains/check?fqdn=free.test").json()["available"] is True

    deleted = auth_client.delete(f"/api/v1/domains/{created.json()['id']}")
    assert deleted.status_code == 204
    assert auth_client.get("/api/v1/domains/check?fqdn=app.dom.test").json()["available"] is True
