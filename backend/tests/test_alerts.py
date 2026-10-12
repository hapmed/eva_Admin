import uuid
from datetime import UTC, datetime, timedelta

from app.models.subscription import Subscription
from tests.factories import make_client, make_eva, make_installation


def test_expiring_subscription_generates_alert(db_session, auth_client):
    client = make_client(auth_client, "Alert")
    plan = auth_client.post(
        "/api/v1/plans",
        json={"code": "monthly-alert", "name": "M", "billing_period": "monthly"},
    ).json()
    subscription = auth_client.post(
        "/api/v1/subscriptions", json={"client_id": client["id"], "plan_id": plan["id"]}
    ).json()

    # Forzamos un vencimiento cercano (5 días) para provocar la alerta.
    record = db_session.get(Subscription, uuid.UUID(subscription["id"]))
    record.end_date = datetime.now(UTC) + timedelta(days=5)
    db_session.commit()

    alerts = auth_client.get("/api/v1/alerts").json()
    keys = {alert["key"] for alert in alerts}
    assert f"subscription:{subscription['id']}:expiring" in keys

    # Reconocer y resolver.
    key = f"subscription:{subscription['id']}:expiring"
    acked = auth_client.post("/api/v1/alerts/acknowledge", json={"key": key}).json()
    assert acked["status"] == "acknowledged"
    resolved = auth_client.post("/api/v1/alerts/resolve", json={"key": key}).json()
    assert resolved["status"] == "resolved"


def test_missing_backup_alert(auth_client):
    client = make_client(auth_client, "NoBackup")
    eva = make_eva(auth_client, code="nobackup")
    installation = make_installation(auth_client, client["id"], eva["id"]).json()
    record = auth_client.post(
        "/api/v1/databases",
        json={"installation_id": installation["id"], "logical_name": "nobackupdb"},
    ).json()

    alerts = auth_client.get("/api/v1/alerts").json()
    keys = {alert["key"] for alert in alerts}
    assert f"database:{record['id']}:backup" in keys
