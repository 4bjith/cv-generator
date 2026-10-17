import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional

# Context variables for request-scoped correlation
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)


class JSONLogFormatter(logging.Formatter):
    """Machine-readable JSON log formatter for production logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request and correlation IDs if present
        req_id = getattr(record, "request_id", None) or request_id_ctx.get()
        if req_id:
            log_entry["request_id"] = req_id

        usr_id = getattr(record, "user_id", None) or user_id_ctx.get()
        if usr_id:
            log_entry["user_id"] = usr_id

        # Include structured attributes if present in record.__dict__
        for attr in ("event", "method", "path", "status_code", "duration_ms", "error_code", "client_ip"):
            val = getattr(record, attr, None)
            if val is not None:
                log_entry[attr] = val

        # Include exception trace if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(level: str = "INFO", log_format: str = "json") -> None:
    """Configure root and framework loggers."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if log_format.lower() == "json":
        handler.setFormatter(JSONLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
        )

    root_logger.addHandler(handler)

    # Set appropriate levels for 3rd party loggers
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        lib_logger = logging.getLogger(logger_name)
        lib_logger.handlers = [handler]
        lib_logger.propagate = False
        lib_logger.setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """Convenience helper to obtain a named logger."""
    return logging.getLogger(name)
