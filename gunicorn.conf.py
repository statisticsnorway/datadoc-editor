"""Configuration for the Gunicorn server."""

from datadoc_editor.logging_configuration.logging_config import get_log_config

bind = "0.0.0.0:8050"
workers = 1
loglevel = "info"
preload = True
logconfig_dict = get_log_config()
