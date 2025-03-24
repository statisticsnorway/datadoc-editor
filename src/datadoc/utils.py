"""General utilities."""

from __future__ import annotations

import datetime
import importlib

METADATA_DOCUMENT_FILE_SUFFIX = "__DOC.json"


def running_in_notebook() -> bool:
    """Return True if running in Jupyter Notebook."""
    try:
        return bool(get_ipython().__class__.__name__ == "ZMQInteractiveShell")  # type: ignore [name-defined]
    except NameError:
        # The get_ipython method is globally available in ipython interpreters
        # as used in Jupyter. However it is not available in other python
        # interpreters and will throw a NameError. Therefore we're not running
        # in Jupyter.
        return False


def pick_random_port() -> int:
    """Pick a random free port number.

    The function will bind a socket to port 0, and a random free port from
    1024 to 65535 will be selected by the operating system.
    """
    import socket

    with socket.socket() as sock:
        sock.bind(("", 0))
        return int(sock.getsockname()[1])


def get_timestamp_now() -> datetime.datetime:
    """Return a timestamp for the current moment."""
    return datetime.datetime.now(tz=datetime.UTC)


def get_app_version() -> str:
    """Get the version of the Datadoc package."""
    return importlib.metadata.distribution("ssb-datadoc").version
