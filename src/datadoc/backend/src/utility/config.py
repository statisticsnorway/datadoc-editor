"""Configuration management for Datadoc package."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from pprint import pformat
from typing import Literal

from dotenv import dotenv_values
from dotenv import load_dotenv

from datadoc.backend.src.utility.enums import DaplaRegion
from datadoc.backend.src.utility.enums import DaplaService

logging.basicConfig(level=logging.DEBUG, force=True)

logger = logging.getLogger(__name__)

DOT_ENV_FILE_PATH = Path(__file__).parent.joinpath(".env")

JUPYTERHUB_USER = "JUPYTERHUB_USER"
DAPLA_REGION = "DAPLA_REGION"
DAPLA_SERVICE = "DAPLA_SERVICE"

env_loaded = False


# TODO(@tilen1976): necessary for backend?  # noqa: TD003
def _load_dotenv_file() -> None:
    global env_loaded  # noqa: PLW0603
    if not env_loaded and DOT_ENV_FILE_PATH.exists():
        load_dotenv(DOT_ENV_FILE_PATH)
        env_loaded = True
        logger.info(
            "Loaded .env file with config keys: \n%s",
            pformat(list(dotenv_values(DOT_ENV_FILE_PATH).keys())),
        )


def _get_config_item(item: str) -> str | None:
    """Get a config item. Makes sure all access is logged."""
    _load_dotenv_file()
    value = os.getenv(item)
    logger.debug("Config accessed. %s", item)
    return value


def get_jupyterhub_user() -> str | None:
    """Get the JupyterHub user name."""
    return _get_config_item(JUPYTERHUB_USER)


# TODO(@tilen1976): necessary for backend?  # noqa: TD003
def get_datadoc_dataset_path() -> str | None:
    """Get the path to the dataset."""
    return _get_config_item("DATADOC_DATASET_PATH")


# TODO(@tilen1976): add logger config?  # noqa: TD003
def get_log_level() -> int:
    """Get the log level."""
    # Magic numbers as defined in Python's stdlib logging
    log_levels: dict[str, int] = {
        "CRITICAL": 50,
        "ERROR": 40,
        "WARNING": 30,
        "INFO": 20,
        "DEBUG": 10,
    }
    if level_string := _get_config_item("DATADOC_LOG_LEVEL"):
        try:
            return log_levels[level_string.upper()]
        except KeyError:
            return log_levels["INFO"]
    else:
        return log_levels["INFO"]


# TODO(@tilen1976): add logger config?  # noqa: TD003
def get_log_formatter() -> Literal["simple", "json"]:
    """Get log formatter configuration."""
    if (
        _get_config_item("DATADOC_ENABLE_JSON_FORMATTING") == "True"
        or get_dapla_region() is not None
    ):
        return "json"
    return "simple"


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_dash_development_mode() -> bool:
    """Get the development mode for Dash."""
    return _get_config_item("DATADOC_DASH_DEVELOPMENT_MODE") == "True"


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_jupyterhub_service_prefix() -> str | None:
    """Get the JupyterHub service prefix."""
    return _get_config_item("JUPYTERHUB_SERVICE_PREFIX")


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_app_name() -> str:
    """Get the name of the app. Defaults to 'Datadoc'."""
    return _get_config_item("DATADOC_APP_NAME") or "Datadoc"


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_jupyterhub_http_referrer() -> str | None:
    """Get the JupyterHub http referrer."""
    return _get_config_item("JUPYTERHUB_HTTP_REFERER")


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_port() -> int:
    """Get the port to run the app on."""
    return int(_get_config_item("DATADOC_PORT") or 7002)


def get_statistical_subject_source_url() -> str | None:
    """Get the URL to the statistical subject source."""
    return _get_config_item("DATADOC_STATISTICAL_SUBJECT_SOURCE_URL")


def get_dapla_region() -> DaplaRegion | None:
    """Get the Dapla region we're running on."""
    if region := _get_config_item(DAPLA_REGION):
        return DaplaRegion(region)

    return None


def get_dapla_service() -> DaplaService | None:
    """Get the Dapla service we're running on."""
    if service := _get_config_item(DAPLA_SERVICE):
        return DaplaService(service)

    return None


def get_oidc_token() -> str | None:
    """Get the JWT token from the environment."""
    return _get_config_item("OIDC_TOKEN")


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_unit_code() -> int | None:
    """The code for the Unit Type code list in Klass."""
    return int(_get_config_item("DATADOC_UNIT_CODE") or 702)


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_measurement_unit_code() -> int | None:
    """The code for the Measurement Unit code list in Klass."""
    return int(_get_config_item("DATADOC_MEASUREMENT_UNIT") or 303)


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_organisational_unit_code() -> int | None:
    """The code for the organisational units code list in Klass."""
    return int(_get_config_item("DATADOC_ORGANISATIONAL_UNIT_CODE") or 83)


# TODO(@tilen1976): remove backend?  # noqa: TD003
def get_data_source_code() -> int | None:
    """The code for the organisational units code list in Klass."""
    return int(_get_config_item("DATADOC_DATA_SOURCE_CODE") or 712)
