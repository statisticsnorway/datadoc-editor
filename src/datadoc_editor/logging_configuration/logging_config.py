from __future__ import annotations

from typing import Any

from datadoc_editor.config import get_log_formatter
from datadoc_editor.config import get_log_level
from datadoc_editor.logging_configuration.gunicorn_access_log_filter import (
    GunicornAccessLoggerHealthProbeFilter,
)


def get_log_config() -> dict[str, Any]:
    """Configure logging for the application."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s",
                "logger": "name",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "datadoc_editor.logging_configuration.json_formatter.DatadocJSONFormatter",
                "fmt_keys": {
                    "level": "levelname",
                    "message": "message",
                    "timestamp": "timestamp",
                    "logger": "name",
                    "module": "module",
                    "function": "funcName",
                    "line": "lineno",
                    "thread_name": "threadName",
                },
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": get_log_level(),
                "formatter": get_log_formatter(),
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "gunicorn": {
                "handlers": ["stdout"],
                "level": "INFO",
                "propagate": False,
            },
            "gunicorn.access": {
                "handlers": ["stdout"],
                "level": "INFO",
                "propagate": False,
                "filters": [GunicornAccessLoggerHealthProbeFilter()],
            },
            "gunicorn.error": {
                "handlers": ["stdout"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "level": get_log_level(),
            "handlers": [
                "stdout",
            ],
        },
    }
