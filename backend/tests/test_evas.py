def test_eva_and_versions(auth_client):
    eva = auth_client.post("/api/v1/evas", json={"code": "cotizaciones", "name": "Cotizaciones y propuestas"})
    assert eva.status_code == 201, eva.text
    eva_id = eva.json()["id"]

    version = auth_client.post(
        f"/api/v1/evas/{eva_id}/versions",
        json={"version": "1.0.0", "deployment_requirements": {"ports": [8000]}},
    )
    assert version.status_code == 201
    assert version.json()["status"] == "approved"

    duplicate = auth_client.post(f"/api/v1/evas/{eva_id}/versions", json={"version": "1.0.0"})
    assert duplicate.status_code == 409

    detail = auth_client.get(f"/api/v1/evas/{eva_id}").json()
    assert [item["version"] for item in detail["versions"]] == ["1.0.0"]


def test_duplicate_eva_code_conflict(auth_client):
    payload = {"code": "unique-code", "name": "EVA"}
    assert auth_client.post("/api/v1/evas", json=payload).status_code == 201
    assert auth_client.post("/api/v1/evas", json=payload).status_code == 409
