"""Logging estructurado y saneado (sin secretos).

Fase 2 define el logger y un filtro de redacción básico. La integración con un
colector y la rotación se completan en fases posteriores (ver OPERATIONS.md).
"""

import logging
import sys

_SENSITIVE_SUBSTRINGS = (
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "cookie",
    "set-cookie",
    "database_url",
)

_redaction_filter = None


class RedactionFilter(logging.Filter):
    """Sustituye valores de claves sensibles presentes en los argumentos."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        try:
            message = record.getMessage()
        except Exception:  # pragma: no cover - defensivo
            return True
        lowered = message.lower()
        if any(hint in lowered for hint in _SENSITIVE_SUBSTRINGS):
            record.msg = "[redacted: mensaje contenía una clave sensible]"
            record.args = ()
        return True


def configure_logging(level: str = "INFO") -> None:
    global _redaction_filter
    if _redaction_filter is None:
        _redaction_filter = RedactionFilter()
    root = logging.getLogger()
    root.setLevel(level)
    for handler in list(root.handlers):
        root.removeHandler(handler)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    handler.addFilter(_redaction_filter)
    root.addHandler(handler)
