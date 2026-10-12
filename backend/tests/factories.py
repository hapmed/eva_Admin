"""Fábricas para pruebas de Fase 4."""


def make_client(auth_client, name: str) -> dict:
    response = auth_client.post("/api/v1/clients", json={"legal_name": name, "display_name": name})
    assert response.status_code == 201, response.text
    return response.json()


def make_eva(
    auth_client,
    code: str,
    config_schema: dict | None = None,
    version: str = "1.0.0",
    version_status: str = "approved",
) -> dict:
    eva = auth_client.post(
        "/api/v1/evas", json={"code": code, "name": code, "config_schema": config_schema or {}}
    )
    assert eva.status_code == 201, eva.text
    eva_body = eva.json()
    version_response = auth_client.post(
        f"/api/v1/evas/{eva_body['id']}/versions",
        json={"version": version, "status": version_status},
    )
    assert version_response.status_code == 201, version_response.text
    return eva_body


def make_installation(
    auth_client,
    client_id: str,
    eva_id: str,
    *,
    desired_version: str = "1.0.0",
    config: dict | None = None,
    primary_domain: str | None = None,
    secrets: list[dict] | None = None,
    idempotency_key: str | None = None,
):
    payload: dict = {
        "client_id": client_id,
        "eva_product_id": eva_id,
        "desired_version": desired_version,
        "config": config or {},
        "secrets": secrets or [],
    }
    if primary_domain:
        payload["primary_domain"] = primary_domain
    if idempotency_key:
        payload["idempotency_key"] = idempotency_key
    return auth_client.post("/api/v1/installations", json=payload)
