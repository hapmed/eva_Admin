from app.core.config import get_settings
from tests.conftest import make_user


def test_login_rate_limit(monkeypatch, client, db_session):
    make_user(db_session, "rl@hapmed.test", "rl-password", ["read_only"])
    monkeypatch.setenv("EVAS_RATE_LIMIT_AUTH_PER_MINUTE", "3")
    get_settings.cache_clear()

    codes = [
        client.post("/api/v1/auth/login", json={"email": "rl@hapmed.test", "password": "bad"}).status_code
        for _ in range(6)
    ]
    assert 429 in codes
