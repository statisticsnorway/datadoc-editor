"""Functions which aren't directly called from a decorated callback."""

from __future__ import annotations

import datetime
import json
import logging
import re
import warnings
from typing import TYPE_CHECKING

import arrow
import ssb_dash_components as ssb
from dapla_metadata.datasets import Datadoc
from dapla_metadata.datasets import ObligatoryDatasetWarning
from dapla_metadata.datasets import ObligatoryVariableWarning
from dapla_metadata.datasets import model
from dash import html

from datadoc_editor import config
from datadoc_editor import state
from datadoc_editor.constants import CHECK_OBLIGATORY_METADATA_DATASET_MESSAGE
from datadoc_editor.constants import CHECK_OBLIGATORY_METADATA_VARIABLES_MESSAGE
from datadoc_editor.constants import ILLEGAL_SHORTNAME_WARNING
from datadoc_editor.constants import ILLEGAL_SHORTNAME_WARNING_MESSAGE
from datadoc_editor.constants import MISSING_METADATA_WARNING
from datadoc_editor.frontend.components.builders import AlertTypes
from datadoc_editor.frontend.components.builders import build_ssb_alert
from datadoc_editor.frontend.components.identifiers import ACCORDION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import SECTION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import VARIABLES_INFORMATION_ID
from datadoc_editor.frontend.fields.display_dataset import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS_AND_DISPLAY_NAME,
)
from datadoc_editor.frontend.fields.display_variables import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_AND_DISPLAY_NAME,
)

if TYPE_CHECKING:
    import pathlib

    import dash_bootstrap_components as dbc
    import pydantic
    from cloudpathlib import CloudPath


logger = logging.getLogger(__name__)


MetadataInputTypes = str | list[str] | int | float | bool | datetime.date | None


def _check_if_language_string_item_exists(
    language_strings: model.LanguageStringType,
    language_code: str,
) -> bool:
    if language_strings.root is None:
        return False
    return any(i.languageCode == language_code for i in language_strings.root)


def _update_language_string_item(
    language_strings: model.LanguageStringType,
    language_code: str,
    new_value: str,
) -> None:
    if language_strings.root is not None:
        for i in language_strings.root:
            if i.languageCode == language_code:
                i.languageText = new_value


def _add_language_string_item(
    language_strings: model.LanguageStringType,
    language_code: str,
    language_text: str,
) -> None:
    if language_strings.root is not None:
        language_strings.root.append(
            model.LanguageStringTypeItem(
                languageCode=language_code,
                languageText=language_text,
            ),
        )


def find_existing_language_string(
    metadata_model_object: pydantic.BaseModel,
    value: str,
    metadata_identifier: str,
    language: str,
) -> model.LanguageStringType | None:
    """Get or create a LanguageStrings object and return it."""
    language_strings = getattr(metadata_model_object, metadata_identifier)

    if language_strings is not None:
        if _check_if_language_string_item_exists(
            language_strings,
            language,
        ):
            _update_language_string_item(
                language_strings,
                language,
                value,
            )
        elif value != "":
            _add_language_string_item(
                language_strings,
                language,
                value,
            )
        else:
            return None
    elif value != "":
        language_strings = model.LanguageStringType(
            root=[
                model.LanguageStringTypeItem(
                    languageCode=language,
                    languageText=value,
                ),
            ],
        )
    else:
        # Don't create an item if the value is empty
        return None
    return language_strings


def get_dataset_path() -> pathlib.Path | CloudPath | str:
    """Extract the path to the dataset from the potential sources."""
    if state.metadata.dataset_path is not None:
        return state.metadata.dataset_path
    path_from_env = config.get_datadoc_dataset_path()
    if path_from_env:
        logger.info(
            "Dataset path from env var: '%s'",
            path_from_env,
        )
    if path_from_env is None:
        path_from_env = ""
    return path_from_env


VALIDATION_ERROR = "Validation error: "
DATE_VALIDATION_MESSAGE = f"{VALIDATION_ERROR}contains_data_from must be the same or earlier date than contains_data_until"


def parse_and_validate_dates(
    start_date: str | datetime.datetime | None,
    end_date: str | datetime.datetime | None,
) -> tuple[datetime.datetime | None, datetime.datetime | None]:
    """Parse and validate the given dates.

    Validate that:
        - The dates are in YYYY-MM-DD format
        - The start date is earlier or identical to the end date.

    Examples:
    >>> parse_and_validate_dates("2021-01-01", "2021-01-01")
    (datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))

    >>> parse_and_validate_dates("1990-01-01", "2050-01-01")
    (datetime.datetime(1990, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2050, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))

    >>> parse_and_validate_dates(None, None)
    (None, None)

    >>> parse_and_validate_dates("1st January 2021", "1st January 2021")
    Traceback (most recent call last):
    ...
    ValueError: Validation error: Expected an ISO 8601-like string, but was given '1st January 2021'. Try passing in a format string to resolve this.

    >>> parse_and_validate_dates(datetime.datetime(2050, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "1990-01-01")
    Traceback (most recent call last):
    ...
    ValueError: Validation error: contains_data_from must be the same or earlier date than contains_data_until

    >>> parse_and_validate_dates("2050-01-01", "1990-01-01")
    Traceback (most recent call last):
    ...
    ValueError: Validation error: contains_data_from must be the same or earlier date than contains_data_until
    """
    parsed_start = None
    parsed_end = None
    try:
        if start_date and start_date != "None":
            parsed_start = arrow.get(start_date)
        if end_date and end_date != "None":
            parsed_end = arrow.get(end_date)
    except arrow.parser.ParserError as e:
        raise ValueError(VALIDATION_ERROR + str(e)) from e

    if parsed_start and parsed_end and (parsed_start > parsed_end):
        raise ValueError(DATE_VALIDATION_MESSAGE)

    start_output = parsed_start.astimezone(tz=datetime.UTC) if parsed_start else None
    end_output = parsed_end.astimezone(tz=datetime.UTC) if parsed_end else None

    return start_output, end_output


def render_tabs(tab: str) -> html.Article | None:
    """Render tab content."""
    if tab == "dataset":
        return html.Article(
            [
                html.Article(
                    id=SECTION_WRAPPER_ID,
                    className="workspace-content",
                ),
            ],
            className="workspace-page-wrapper",
        )
    if tab == "variables":
        return html.Article(
            [
                html.Header(
                    [
                        ssb.Paragraph(
                            id=VARIABLES_INFORMATION_ID,
                            className="workspace-info-paragraph",
                        ),
                        ssb.Input(
                            label="Filtrer",
                            searchField=True,
                            disabled=False,
                            placeholder="Variabel kortnavn...",
                            id="search-variables",
                            n_submit=0,
                            value="",
                        ),
                    ],
                    className="workspace-header",
                ),
                html.Article(
                    id=ACCORDION_WRAPPER_ID,
                    className="workspace-content",
                ),
            ],
            className="workspace-page-wrapper",
        )

    return None


def _has_exact_word(word: str, text: str) -> bool:
    """Return True if excact word matches text."""
    return bool(re.search(rf"\b{word}\b", text))


def dataset_control(error_message: str | None) -> dbc.Alert | None:
    """Check obligatory metadata values for dataset.

    Args:
        error_message(str): A message generated by ObligatoryDatasetWarning containing names of fields missing value.
    """
    missing_metadata = [
        f[1]
        for f in OBLIGATORY_DATASET_METADATA_IDENTIFIERS_AND_DISPLAY_NAME
        if (error_message and _has_exact_word(f[0], error_message))
    ]
    if not missing_metadata:
        return None
    return build_ssb_alert(
        AlertTypes.WARNING,
        MISSING_METADATA_WARNING,
        CHECK_OBLIGATORY_METADATA_DATASET_MESSAGE,
        None,
        missing_metadata,
    )


def _parse_error_message(message: str) -> list | None:
    """Parse a string containing an error message into Python objects.

    This function processes an error message by removing predefined text and
    attempting to parse the remaining string into a list of Python objects.

    Args:
        message (str): The error message string to be parsed.

    Returns:
        A list of parsed objects if the string can be successfully parsed.
        returns None if the string is empty after processing and a empty list
        if the string cannot be parsed into JSON.
    """
    parsed_string = message.replace("Obligatory metadata is missing: ", "").strip()
    parsed_string = parsed_string.replace("'", '"')
    if not parsed_string:
        return None
    try:
        # Attempt to parse the JSON string
        return json.loads(parsed_string)
    except json.JSONDecodeError:
        logger.exception("Error parsing JSON {e}")
        return []


def _get_dict_by_key(
    metadata_list: list[dict[str, list[str]]],
    key: str,
) -> dict[str, list[str]] | None:
    """Return the first dictionary containing the specified key.

    This function searches through a list of dictionaries and returns the first
    dictionary that contains the specified key.

    Args:
        metadata_list: A list of dictionaries to search.
        key: The key to search for in each dictionary.

    Returns:
        The first dictionary containing the specified key,
        or None if no such dictionary is found.

    """
    return next((item for item in metadata_list if key in item), None)


def variables_control(error_message: str | None, variables: list) -> dbc.Alert | None:
    """Check obligatory metadata for variables and return an alert if any metadata is missing.

    This function parses an error message to identify missing obligatory metadata
    fields for variables. If missing metadata is found, it generates an alert.

    Args:
        error_message: A message generated by ObligatoryVariableWarning
            containing the variable short name and a list of field names with missing values.
        variables: list of datadoc variables

    Returns:
        An alert object if there are missing metadata fields, otherwise None.
    """
    missing_metadata: list = []
    error_message_parsed = _parse_error_message(str(error_message))
    # for variable in state.metadata.variables:
    for variable in variables:
        if error_message_parsed:
            fields_by_variable = _get_dict_by_key(
                error_message_parsed,
                variable.short_name,
            )
            if fields_by_variable is not None:
                missing_metadata_field = [
                    f[1]
                    for f in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_AND_DISPLAY_NAME
                    if error_message and f[0] in fields_by_variable[variable.short_name]
                ]
                missing_metadata_fields_to_string = ", ".join(missing_metadata_field)
                missing_metadata.append(
                    f"{variable.short_name}: {missing_metadata_fields_to_string}",
                )
    if not missing_metadata:
        return None
    return build_ssb_alert(
        AlertTypes.WARNING,
        MISSING_METADATA_WARNING,
        CHECK_OBLIGATORY_METADATA_VARIABLES_MESSAGE,
        None,
        missing_metadata,
    )


def check_variable_names(
    variables: list,
) -> dbc.Alert | None:
    """Checks if a variable shortname complies with the naming standard.

    Returns:
        An ssb alert with a message saying that what names dont comply with the naming standard.
    """
    illegal_names: list = [
        v.short_name
        for v in variables
        if not re.match(r"^[a-z0-9_]{3,}$", v.short_name)
    ]

    if not illegal_names:
        return None
    return build_ssb_alert(
        AlertTypes.WARNING,
        ILLEGAL_SHORTNAME_WARNING,
        ILLEGAL_SHORTNAME_WARNING_MESSAGE,
        None,
        illegal_names,
    )


def save_metadata_and_generate_alerts(metadata: Datadoc) -> list:
    """Save the metadata document to disk and check obligatory metadata.

    Returns:
        List of alerts including obligatory metadata warnings if missing,
        and success alert if metadata is saved correctly.
    """
    missing_obligatory_dataset = ""
    missing_obligatory_variables = ""

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            metadata.write_metadata_document()
            success_alert = build_ssb_alert(
                AlertTypes.SUCCESS,
                "Lagret metadata",
            )
            for warning in w:
                if issubclass(warning.category, ObligatoryDatasetWarning):
                    missing_obligatory_dataset = str(warning.message)
                elif issubclass(warning.category, ObligatoryVariableWarning):
                    missing_obligatory_variables = str(warning.message)
                else:
                    logger.warning(
                        "An unexpected warning was caught: %s",
                        warning.message,
                    )
        except (ValueError, FileNotFoundError) as e:
            if isinstance(e, ValueError):
                logger.exception("Unable to save metadata document, no dataset found")
            elif isinstance(e, FileNotFoundError):
                logger.exception(
                    "Unable to save metadata document, file %s not found",
                    metadata.dataset_path,
                )
            success_alert = build_ssb_alert(
                AlertTypes.ERROR,
                "Kunne ikke lagre metadata",
            )

    return [
        success_alert,
        dataset_control(missing_obligatory_dataset),
        variables_control(missing_obligatory_variables, metadata.variables),
        check_variable_names(metadata.variables),
    ]
