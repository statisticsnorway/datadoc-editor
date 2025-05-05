from __future__ import annotations

import datetime as dt
import json
import logging
from typing import Any


class DatadocJSONFormatter(logging.Formatter):
    """Class for formatting json for log files."""

    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ) -> None:
        """Initializer for the json formatter."""
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    def format(self, record: logging.LogRecord) -> str:
        """Method that creates the json structure from a message created by the _prepare_log_dict method."""
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict[str, str | Any]:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created,
                tz=dt.UTC,
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: (
                msg_val
                if (msg_val := always_fields.pop(val, None)) is not None
                else getattr(record, val)
            )
            for key, val in self.fmt_keys.items()
        }

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in message
            and key not in always_fields
            and key
            not in (
                "pathname",
                "filename",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "processName",
                "process",
                "taskName",
                "levelno",
                "args",
                "msg",
                "levelname",
                "name",
            )
        }

        message.update(always_fields)
        message.update(extra_fields)

        return message
