from app.db.bootstrap import ensure_superadmin


def test_ensure_superadmin_idempotent(db_session):
    user = ensure_superadmin(db_session, "root@hapmed.test", "root-password")
    assert user is not None
    assert [role.code for role in user.roles] == ["superadmin"]

    again = ensure_superadmin(db_session, "root@hapmed.test", "root-password")
    assert again.id == user.id


def test_ensure_superadmin_noop_without_credentials(db_session):
    assert ensure_superadmin(db_session, "", "") is None
