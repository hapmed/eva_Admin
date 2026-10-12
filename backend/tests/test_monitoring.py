from sqlalchemy import select

from app.models.monitoring import Backup
from tests.factories import make_client, make_eva, make_installation


def _installation(auth_client, name: str = "Mon"):
    client = make_client(auth_client, name)
    eva = make_eva(auth_client, code=f"mon-{name.lower()}")
    return make_installation(auth_client, client["id"], eva["id"]).json()


def test_health_check_records_service_state(auth_client):
    installation = _installation(auth_client, "Health")
    assert len(installation["services"]) == 1

    response = auth_client.post(f"/api/v1/installations/{installation['id']}/health-check")
    assert response.status_code == 200
    assert response.json()["type"] == "health_check"
    assert response.json()["simulated"] is True

    health = auth_client.get(f"/api/v1/installations/{installation['id']}/health").json()
    assert len(health["services"]) == 1
    assert health["services"][0]["last_checked_at"] is not None


def test_logs_and_metrics_are_simulated_and_empty(auth_client):
    installation = _installation(auth_client, "Logs")
    logs = auth_client.get(f"/api/v1/installations/{installation['id']}/logs").json()
    assert logs["simulated"] is True
    assert logs["lines"] == []

    metrics = auth_client.get(f"/api/v1/installations/{installation['id']}/metrics").json()
    assert metrics["simulated"] is True
    assert metrics["samples"] == []


def test_upgrade_creates_simulated_backup(db_session, auth_client):
    client = make_client(auth_client, "BackupUp")
    eva = make_eva(auth_client, code="backupup", version="1.0.0")
    auth_client.post(f"/api/v1/evas/{eva['id']}/versions", json={"version": "1.1.0"})
    installation = make_installation(auth_client, client["id"], eva["id"]).json()
    auth_client.post(
        "/api/v1/databases",
        json={"installation_id": installation["id"], "logical_name": "backupdb"},
    )

    response = auth_client.post(
        f"/api/v1/installations/{installation['id']}/upgrade",
        json={"target_version": "1.1.0"},
    )
    assert response.status_code == 200

    backups = db_session.scalars(select(Backup)).all()
    assert len(backups) == 1
    assert backups[0].status == "simulated"
