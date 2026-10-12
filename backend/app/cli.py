"""Comandos de línea de comandos de EVAS Admin.

Uso:
    python -m app.cli notify-alerts
"""

import argparse

from app.db.session import get_session_factory
from app.services import notifications


def _notify_alerts() -> None:
    session = get_session_factory()()
    try:
        count = notifications.notify_alerts(session)
    finally:
        session.close()
    print(f"alertas notificadas: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="evas-admin")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("notify-alerts", help="Envía por email las alertas abiertas")
    args = parser.parse_args()

    if args.command == "notify-alerts":
        _notify_alerts()


if __name__ == "__main__":
    main()
