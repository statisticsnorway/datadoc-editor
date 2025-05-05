"""Entrypoint for Gunicorn."""

import concurrent

from .app import get_app

with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
    datadoc_app, _ = get_app(executor)
    server = datadoc_app.server
