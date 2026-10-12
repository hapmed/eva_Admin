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
        "eva_products",
        "eva_versions",
        "plans",
        "subscriptions",
        "subscription_events",
        "audit_logs",
        "nodes",
        "installations",
        "installation_services",
        "domains",
        "database_records",
        "installation_configs",
        "secret_references",
        "operations",
        "health_checks",
        "metrics",
        "backups",
        "alert_states",
        "webauthn_credentials",
    }
    assert expected <= tables
