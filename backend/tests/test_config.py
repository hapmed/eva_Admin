from app.core.config import Settings


def test_defaults_are_fictitious():
    settings = Settings()
    assert settings.db_password == "change-me-in-env"
    assert settings.agent_mode == "simulated"
    assert settings.is_local is True


def test_database_url_shape():
    settings = Settings(
        db_host="h", db_port=5432, db_user="u", db_password="p", db_name="d"
    )
    url = settings.database_url
    assert url.startswith("postgresql+psycopg://")
    assert url.endswith("/d?sslmode=prefer")


def test_env_prefix_override(monkeypatch):
    monkeypatch.setenv("EVAS_DB_HOST", "example.internal")
    monkeypatch.setenv("EVAS_ENVIRONMENT", "prod")
    settings = Settings()
    assert settings.db_host == "example.internal"
    assert settings.is_local is False
