"""Notificaciones por email (SMTP) de las alertas abiertas.

Sin dependencias externas: usa `smtplib`. Nunca registra credenciales.
"""

import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services import alerts_service


def send_email(subject: str, body: str) -> bool:
    settings = get_settings()
    if not settings.smtp_enabled or not settings.smtp_host or not settings.smtp_to:
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = ", ".join(settings.smtp_to)
    message.set_content(body)

    if settings.smtp_ssl:
        server: smtplib.SMTP = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20)
    else:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20)
    try:
        if settings.smtp_starttls and not settings.smtp_ssl:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)
    finally:
        server.quit()
    return True


def build_digest(alerts: list[dict]) -> tuple[str, str]:
    open_alerts = [alert for alert in alerts if alert.get("status") == "open"]
    if not open_alerts:
        return "", ""
    subject = f"[EVAS Admin] {len(open_alerts)} alerta(s) abierta(s)"
    lines = [
        f"- [{alert['severity']}] {alert['message']} ({alert['type']})"
        for alert in open_alerts
    ]
    body = "Alertas abiertas en EVAS Admin:\n\n" + "\n".join(lines) + "\n"
    return subject, body


def notify_alerts(db: Session) -> int:
    """Envía por email las alertas abiertas. Devuelve cuántas se notificaron."""
    alerts = alerts_service.compute_alerts(db)
    subject, body = build_digest(alerts)
    if not subject:
        return 0
    if not send_email(subject, body):
        return 0
    return len([alert for alert in alerts if alert.get("status") == "open"])
