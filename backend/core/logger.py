"""
Structured logging utilities configured for async-friendly operation.
"""

from __future__ import annotations

import json
import logging
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Optional

from .config import get_settings

_queue: Optional[Queue] = None
_listener: Optional[QueueListener] = None
_configured = False


def _build_logging_config(log_level: str, json_logs: bool) -> dict:
    base_format = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s | %(correlation_id)s"
    )
    if json_logs:
        formatter = {
            "format": json.dumps(
                {
                    "timestamp": "%(asctime)s",
                    "level": "%(levelname)s",
                    "logger": "%(name)s",
                    "message": "%(message)s",
                    "correlation_id": "%(correlation_id)s",
                }
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        }
    else:
        formatter = {"format": base_format, "datefmt": "%Y-%m-%d %H:%M:%S"}

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": formatter,
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
    }


class AsyncQueueListener(QueueListener):
    """Queue listener that ensures graceful shutdown."""

    def stop(self) -> None:
        try:
            super().stop()
        finally:
            while not self.queue.empty():
                self.queue.get_nowait()


def configure_logging() -> None:
    """Configure logging only once, using an async-friendly queue handler."""

    global _queue, _listener, _configured

    if _configured:
        return

    settings = get_settings()
    config = _build_logging_config(settings.log_level.upper(), settings.log_json)

    dictConfig(config)

    _queue = Queue(-1)
    queue_handler = QueueHandler(_queue)
    root_logger = logging.getLogger()
    root_logger.handlers = [queue_handler]

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s | %(correlation_id)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    _listener = AsyncQueueListener(_queue, console_handler)
    _listener.start()

    _configured = True


class CorrelationIdFilter(logging.Filter):
    """Ensure every record provides a correlation id field for formatting."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "-"
        return True


def get_logger(name: str) -> logging.Logger:
    """Return a logger with consistent configuration."""

    configure_logging()
    logger = logging.getLogger(name)
    logger.addFilter(CorrelationIdFilter())
    return logger


def shutdown_logging() -> None:
    """Stop the queue listener on application shutdown."""

    global _listener, _configured
    if _listener:
        _listener.stop()
    _configured = False

