"""Logs estruturados em JSON (um objeto JSON por linha, em stdout)."""
import contextvars
import json
import logging
import sys
from datetime import datetime, timezone

# Identificador da requisição atual, disponível para qualquer log emitido durante ela.
request_id_var: contextvars.ContextVar = contextvars.ContextVar("request_id", default=None)

_EXTRA_FIELDS = ("operation", "orderId", "method", "path", "status", "durationMs")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "message": record.getMessage(),
            "requestId": request_id_var.get(),
        }
        for key in _EXTRA_FIELDS:
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("pedidos")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
