"""Fixtures compartidas de pruebas."""

import pytest


@pytest.fixture
def settings_env(monkeypatch):
    """Variables de entorno ficticias para pruebas de configuración."""
    monkeypatch.setenv("EVAS_ENVIRONMENT", "test")
    monkeypatch.setenv("EVAS_DB_HOST", "db.test.internal")
    return monkeypatch
