import logging

EXCLUDED_PATHS = ["/healthz", "/_dash-", "/assets"]


class GunicornAccessLoggerHealthProbeFilter(logging.Filter):
    """Filter out any Gunicorn access logs on Liveness or Readiness probes."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter health probes on the /healthz endpoints."""
        return all(path not in record.getMessage() for path in EXCLUDED_PATHS)
