import app.models  # noqa: F401  (registra los modelos)
from app.db.base import Base


def test_expected_tables_registered():
    tables = set(Base.metadata.tables)
    expected = {
        "hapmed_users",
        "roles",
        "permissions",
        "hapmed_user_roles",
        "role_permissions",
        "clients",
        "client_users",
        "api_tokens",
    }
    assert expected <= tables
