from tests.factories import make_client, make_eva, make_installation


def test_database_metadata_and_backup(auth_client):
    client = make_client(auth_client, "Db")
    eva = make_eva(auth_client, code="dbx")
    installation = make_installation(auth_client, client["id"], eva["id"]).json()

    record = auth_client.post(
        "/api/v1/databases",
        json={"installation_id": installation["id"], "logical_name": "alfadb", "host_ref": "node-1"},
    )
    assert record.status_code == 201, record.text
    body = record.json()
    assert body["engine"] == "postgresql"
    assert body["last_backup_at"] is None
    assert "password" not in record.text.lower()

    backup = auth_client.post(f"/api/v1/databases/{body['id']}/backup", json={})
    assert backup.status_code == 200
    assert backup.json()["type"] == "request_backup"
    assert backup.json()["simulated"] is True

    restore = auth_client.post(f"/api/v1/databases/{body['id']}/restore", json={"backup_ref": "backup-1"})
    assert restore.status_code == 200
    assert restore.json()["type"] == "request_restore"
