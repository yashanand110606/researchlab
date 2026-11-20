"""Structured logging configuration."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(level)
