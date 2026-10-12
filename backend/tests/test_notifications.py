from app.services import notifications


def test_build_digest_empty():
    assert notifications.build_digest([]) == ("", "")
    assert notifications.build_digest([{"status": "resolved"}]) == ("", "")


def test_build_digest_formats_open_alerts():
    alerts = [
        {"status": "open", "severity": "warning", "message": "Vence pronto", "type": "subscription_expiring"},
        {"status": "resolved", "severity": "critical", "message": "x", "type": "y"},
    ]
    subject, body = notifications.build_digest(alerts)
    assert "1 alerta" in subject
    assert "Vence pronto" in body
    assert "resolved" not in body


def test_send_email_disabled_returns_false():
    assert notifications.send_email("s", "b") is False
