def _create_client(auth_client, name: str) -> dict:
    return auth_client.post("/api/v1/clients", json={"legal_name": name, "display_name": name}).json()


def test_plan_and_subscription_lifecycle(auth_client):
    plan = auth_client.post(
        "/api/v1/plans",
        json={
            "code": "monthly",
            "name": "Mensual",
            "billing_period": "monthly",
            "price": "10.00",
            "currency": "USD",
        },
    )
    assert plan.status_code == 201, plan.text
    client = _create_client(auth_client, "Suscripciones S.L.")

    subscription = auth_client.post(
        "/api/v1/subscriptions",
        json={"client_id": client["id"], "plan_id": plan.json()["id"]},
    )
    assert subscription.status_code == 201, subscription.text
    body = subscription.json()
    assert body["status"] == "active"
    assert 27 <= body["days_to_expiry"] <= 31
    assert body["expiring_soon"] is False
    subscription_id = body["id"]

    events = auth_client.get(f"/api/v1/subscriptions/{subscription_id}/events").json()
    assert [event["event_type"] for event in events] == ["created"]

    renewed = auth_client.post(
        f"/api/v1/subscriptions/{subscription_id}/renew", json={"notes": "renovación anual"}
    )
    assert renewed.status_code == 200, renewed.text
    assert renewed.json()["days_to_expiry"] > body["days_to_expiry"]

    events = auth_client.get(f"/api/v1/subscriptions/{subscription_id}/events").json()
    assert [event["event_type"] for event in events] == ["created", "renewed"]

    cancelled = auth_client.post(f"/api/v1/subscriptions/{subscription_id}/cancel", json={})
    assert cancelled.json()["status"] == "cancelled"

    # No se puede renovar una cancelada.
    assert auth_client.post(f"/api/v1/subscriptions/{subscription_id}/renew", json={}).status_code == 409


def test_subscription_isolation_by_client(auth_client):
    plan = auth_client.post(
        "/api/v1/plans", json={"code": "yearly", "name": "Anual", "billing_period": "yearly"}
    ).json()
    client_a = _create_client(auth_client, "Alfa")
    client_b = _create_client(auth_client, "Beta")

    auth_client.post("/api/v1/subscriptions", json={"client_id": client_a["id"], "plan_id": plan["id"]})
    auth_client.post("/api/v1/subscriptions", json={"client_id": client_b["id"], "plan_id": plan["id"]})

    only_a = auth_client.get(f"/api/v1/subscriptions?client_id={client_a['id']}").json()
    assert len(only_a) == 1
    assert only_a[0]["client_id"] == client_a["id"]
