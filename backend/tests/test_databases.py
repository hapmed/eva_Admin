import uuid

from app.models.monitoring import Backup
from tests.factories import make_client, make_eva, make_installation


def _database(auth_client) -> dict:
    client = make_client(auth_client, "Db")
    eva = make_eva(auth_client, code="dbx")
    installation = make_installation(auth_client, client["id"], eva["id"]).json()
    record = auth_client.post(
        "/api/v1/databases",
        json={"installation_id": installation["id"], "logical_name": "alfadb", "host_ref": "node-1"},
    )
    assert record.status_code == 201, record.text
    return record.json()


def test_database_metadata_no_credentials(auth_client):
    body = _database(auth_client)
    assert body["engine"] == "postgresql"
    assert body["last_backup_at"] is None


def test_backup_registers_copy(auth_client):
    database = _database(auth_client)
    db_id = database["id"]

    backup = auth_client.post(f"/api/v1/databases/{db_id}/backup", json={})
    assert backup.status_code == 200
    assert backup.json()["type"] == "request_backup"

    backups = auth_client.get(f"/api/v1/databases/{db_id}/backups").json()
    assert len(backups) == 1
    assert backups[0]["status"] == "simulated"
    assert backups[0]["location_ref"] is None


def test_restore_requires_file_and_confirmation(db_session, auth_client):
    database = _database(auth_client)
    db_id = database["id"]

    auth_client.post(f"/api/v1/databases/{db_id}/backup", json={})
    simulated = auth_client.get(f"/api/v1/databases/{db_id}/backups").json()[0]

    # Copia simulada (sin fichero) no es restaurable.
    no_file = auth_client.post(
        f"/api/v1/databases/{db_id}/restore",
        json={"backup_ref": simulated["id"], "confirm": "alfadb"},
    )
    assert no_file.status_code == 409

    # Copia real (con fichero): confirmación incorrecta -> 409; correcta -> 200.
    backup = Backup(
        database_record_id=uuid.UUID(db_id),
        type="full",
        status="succeeded",
        location_ref="alfadb/2026.dump",
    )
    db_session.add(backup)
    db_session.commit()
    db_session.refresh(backup)

    bad = auth_client.post(
        f"/api/v1/databases/{db_id}/restore",
        json={"backup_ref": str(backup.id), "confirm": "otro"},
    )
    assert bad.status_code == 409

    ok = auth_client.post(
        f"/api/v1/databases/{db_id}/restore",
        json={"backup_ref": str(backup.id), "confirm": "alfadb"},
    )
    assert ok.status_code == 200
    assert ok.json()["type"] == "request_restore"
