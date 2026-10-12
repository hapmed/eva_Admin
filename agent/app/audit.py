"""Registro de operaciones (auditoría, sin secretos)."""

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("evas.agent.audit")


def record(operation: str, installation_id: str, status: str, **extra: Any) -> None:
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "operation": operation,
        "installation_id": installation_id,
        "status": status,
    }
    entry.update(extra)
    logger.info("agent.operation %s", entry)
