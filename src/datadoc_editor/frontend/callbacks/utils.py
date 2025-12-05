"""Functions which aren't directly called from a decorated callback."""

from __future__ import annotations

import datetime
import json
import logging
import re
import warnings
from typing import TYPE_CHECKING
from typing import cast

import arrow
import ssb_dash_components as ssb
from dapla_metadata.datasets import Datadoc
from dapla_metadata.datasets import ObligatoryDatasetWarning
from dapla_metadata.datasets import ObligatoryVariableWarning
from dapla_metadata.datasets import model
from dash import dcc
from dash import html

from datadoc_editor import config
from datadoc_editor import constants
from datadoc_editor import state
from datadoc_editor.constants import CHECK_OBLIGATORY_METADATA_DATASET_MESSAGE
from datadoc_editor.constants import CHECK_OBLIGATORY_METADATA_VARIABLES_MESSAGE
from datadoc_editor.constants import ILLEGAL_SHORTNAME_WARNING
from datadoc_editor.constants import ILLEGAL_SHORTNAME_WARNING_MESSAGE
from datadoc_editor.constants import MISSING_METADATA_WARNING
from datadoc_editor.constants import PAPIS_STABLE_IDENTIFIER_TYPE
from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.components.builders import AlertTypes
from datadoc_editor.frontend.components.builders import build_ssb_alert
from datadoc_editor.frontend.components.identifiers import ACCORDION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_ID
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_STORE
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_VALUES_STORE
from datadoc_editor.frontend.components.identifiers import SECTION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import VARIABLES_INFORMATION_ID
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_base import MetadataMultiDropdownField
from datadoc_editor.frontend.fields.display_dataset import DISPLAY_DATASET
from datadoc_editor.frontend.fields.display_dataset import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS_AND_DISPLAY_NAME,
)
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    OBLIGATORY_VARIABLES_METADATA_PSEUDO_IDENTIFIERS_AND_DISPLAY_NAME,
)
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_DEAD_METADATA,
)
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_METADATA,
)
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_PAPIS_WITH_STABLE_ID_METADATA,
)
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_PAPIS_WITHOUT_STABLE_ID_METADATA,
)
from datadoc_editor.frontend.fields.display_variables import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_AND_DISPLAY_NAME,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import dash_bootstrap_components as dbc
    import pydantic
    from dapla_metadata.datasets.utility.utils import VariableType
    from upath.types import ReadablePathLike


logger = logging.getLogger(__name__)


MetadataInputTypes = (
    str | list[str] | list[dict] | int | float | bool | datetime.date | None
)
MultidropdownInputTypes = str | None
PseudonymizationInputTypes = str | datetime.datetime | None


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


def update_use_restriction_type(
    metadata_model_object: pydantic.BaseModel,
    value: MultidropdownInputTypes,
    metadata_identifier: str,
    index: int,
) -> list[model.UseRestrictionItem]:
    """Updates the type filed on the in the multidropdown component."""
    items: list[model.UseRestrictionItem] = (
        getattr(metadata_model_object, metadata_identifier, []) or []
    )

    while len(items) <= index:
        items.append(model.UseRestrictionItem())

    items[index].use_restriction_type = (
        model.UseRestrictionType(value) if value else None
    )

    setattr(metadata_model_object, metadata_identifier, items)
    return items


def update_use_restriction_date(
    metadata_model_object: pydantic.BaseModel,
    value: MultidropdownInputTypes,
    metadata_identifier: str,
    index: int,
) -> list[model.UseRestrictionItem]:
    """Updates the date filed on the in the multidropdown component."""
    items: list[model.UseRestrictionItem] = (
        getattr(metadata_model_object, metadata_identifier, []) or []
    )

    while len(items) <= index:
        items.append(model.UseRestrictionItem())

    items[index].use_restriction_date = (
        datetime.datetime.strptime(value, "%Y-%m-%d").date() if value else None  # noqa: DTZ007
    )

    setattr(metadata_model_object, metadata_identifier, items)
    return items


def get_dataset_path() -> ReadablePathLike:
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
                html.Section(
                    id=GLOBAL_VARIABLES_ID,
                    className="",
                ),
                dcc.Store(id=GLOBAL_VARIABLES_VALUES_STORE, data={}),
                dcc.Store(id=GLOBAL_VARIABLES_STORE, data={}),
                html.Article(
                    id=ACCORDION_WRAPPER_ID,
                    className="workspace-content",
                ),
            ],
            className="workspace-page-wrapper",
        )

    return None


def update_store_data_with_inputs(
    store_data: list[dict], type_values: list[str], date_values: list[str]
) -> list[dict]:
    """Update each use restriction in store_data with the latest type/date values."""
    for item, type_val, date_val in zip(
        store_data, type_values, date_values, strict=False
    ):
        item.update(use_restriction_type=type_val, use_restriction_date=date_val)
    return store_data


def render_multidropdown_row(
    item: dict,
    row_id: dict[str, str | int],
    options: Callable[[], list[dict[str, str]]],
    key: str | None = None,
) -> html.Div:
    """Renders a row in the multidropdown component."""
    field = cast(
        "MetadataMultiDropdownField",
        DISPLAY_DATASET[DatasetIdentifiers.USE_RESTRICTIONS],
    )

    dropdown_id = {**row_id, "field": "type"}
    date_id = {**row_id, "field": "date"}
    button_id = {**row_id, "field": "delete"}

    return html.Div(
        [
            ssb.Dropdown(
                header=field.type_display_name,
                items=options,
                placeholder=DROPDOWN_DESELECT_OPTION,
                value=item.get("use_restriction_type"),
                id=dropdown_id,
                className="dropdown-component",
                showDescription=True,
                description=field.type_description,
            ),
            html.Div(
                [
                    ssb.Input(
                        label=field.date_display_name,
                        value=item.get("use_restriction_date"),
                        id=date_id,
                        className="input-component",
                        type="date",
                        showDescription=True,
                        description=field.date_description,
                    ),
                    html.Button(
                        "",
                        id=button_id,
                        # Dict unpacking necessary for wildcard props in Dash
                        **{"aria-label": "Delete row"},  # type: ignore[arg-type]
                        className="multidropdown-delete-button",
                    ),
                ],
                className="date-button-row",
            ),
        ],
        className="input-group-row",
        key=key,
    )


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


def variables_control(
    error_message: list[str] | None, variables: list
) -> dbc.Alert | None:
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
    # NOTE(tilen1976): This is a bug fix - can be fragile. The bug is probably cause by multiple validations which are triggered by "write_metadata_document()"
    # Use first element in variables error messages because there is a second validation which overwrites the result
    error_message_parsed = (
        _parse_error_message(str(error_message[0])) if error_message else None
    )
    obligatory_fields = (
        OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_AND_DISPLAY_NAME
        + OBLIGATORY_VARIABLES_METADATA_PSEUDO_IDENTIFIERS_AND_DISPLAY_NAME
    )
    for variable in variables:
        if error_message_parsed:
            fields_by_variable = _get_dict_by_key(
                error_message_parsed,
                variable.short_name,
            )
            if fields_by_variable is not None:
                missing_metadata_field = [
                    f[1]
                    for f in obligatory_fields
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
        if not re.match(r"^[a-z0-9_]{2,}$", v.short_name)
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
    # Use list so the first error message is not overwritten
    missing_obligatory_variables = []

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
                    missing_obligatory_variables.append(str(warning.message))
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
    logger.debug(
        "Missing variables obligatory fields: %s", missing_obligatory_variables
    )
    return [
        success_alert,
        dataset_control(missing_obligatory_dataset),
        variables_control(missing_obligatory_variables, metadata.variables),
        check_variable_names(metadata.variables),
    ]


def map_selected_algorithm_to_pseudo_fields(
    selected_algorithm: PseudonymizationAlgorithmsEnum | None,
) -> list:
    """Map a PseudonymizationAlgorithms enum value to the correct pseudonymization input list.

    Examples:
    >>> pseudo_fields = map_selected_algorithm_to_pseudo_fields(PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID)
    >>> len(pseudo_fields)
    1
    >>> pseudo_fields = map_selected_algorithm_to_pseudo_fields(PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID)
    >>> len(pseudo_fields)
    2
    >>> pseudo_fields = map_selected_algorithm_to_pseudo_fields(PseudonymizationAlgorithmsEnum.CUSTOM)
    >>> len(pseudo_fields)
    5
    """
    mapping = {
        PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID: PSEUDONYMIZATION_PAPIS_WITHOUT_STABLE_ID_METADATA,
        PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID: PSEUDONYMIZATION_PAPIS_WITH_STABLE_ID_METADATA,
        PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA: PSEUDONYMIZATION_DEAD_METADATA,
        PseudonymizationAlgorithmsEnum.CUSTOM: PSEUDONYMIZATION_METADATA,
    }

    if selected_algorithm is None:
        return []

    return mapping.get(selected_algorithm, [])


def map_dropdown_to_pseudo(
    variable: VariableType,
) -> PseudonymizationAlgorithmsEnum | None:
    """Return dropdown algorithm value for a variable's pseudonymization."""
    if variable.pseudonymization:
        match variable.pseudonymization.encryption_algorithm:
            case constants.PAPIS_ALGORITHM_ENCRYPTION:
                if (
                    variable.pseudonymization.stable_identifier_type
                    == PAPIS_STABLE_IDENTIFIER_TYPE
                ):
                    return PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID
                return PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID
            case constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION:
                return PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA
            case _:
                return PseudonymizationAlgorithmsEnum.CUSTOM
    return None


def apply_pseudonymization(
    variable: VariableType,
    selected_algorithm: PseudonymizationAlgorithmsEnum,
) -> None:
    """Apply a pseudonymization algorithm to a variable.

    Depending on the selected algorithm, this function creates a corresponding
    `Pseudonymization` object and assigns it to `state.metadata` for the given variable.

    For `PAPIS_ALGORITHM_WITH_STABLE_ID`, the `stable_identifier_version` is
    automatically set to today's date.

    Args:
        variable (VariableType): The variable to pseudonymize.
        selected_algorithm (PseudonymizationAlgorithmsEnum): The pseudonymization algorithm to apply.

    Side Effects:
        Modifies `state.metadata` by adding or updating the pseudonymization object
        for the given variable.
    """
    if variable.short_name:
        match selected_algorithm:
            case PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID:
                state.metadata.add_pseudonymization(
                    variable.short_name,
                    model.Pseudonymization(
                        encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
                        pseudonymization_time=None,
                    ),
                )
            case PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID:
                state.metadata.add_pseudonymization(
                    variable.short_name,
                    model.Pseudonymization(
                        encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
                        stable_identifier_type=constants.PAPIS_STABLE_IDENTIFIER_TYPE,
                        pseudonymization_time=None,
                        stable_identifier_version=datetime.datetime.now(datetime.UTC)
                        .date()
                        .isoformat(),
                    ),
                )
            case PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA:
                state.metadata.add_pseudonymization(
                    variable.short_name,
                    model.Pseudonymization(
                        encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION,
                        pseudonymization_time=None,
                    ),
                )
            case PseudonymizationAlgorithmsEnum.CUSTOM:
                state.metadata.add_pseudonymization(
                    variable.short_name,
                    pseudonymization=model.Pseudonymization(
                        encryption_algorithm=None,
                        encryption_key_reference=None,
                        pseudonymization_time=None,
                        stable_identifier_type=None,
                        stable_identifier_version=None,
                        encryption_algorithm_parameters=None,
                    ),
                )


def update_stable_identifier_version(
    field_value: PseudonymizationInputTypes, variable: VariableType
) -> str:
    """Validate and update the stable identifier version for a variable.

    This function validates that `field_value` is a proper date and converts it
    to an ISO-formatted string (`YYYY-MM-DD`). If the variable has an associated
    pseudonymization with `encryption_algorithm_parameters`, it updates the
    `snapshotDate` in the corresponding dictionary.

    Args:
        field_value (PseudonymizationInputTypes): The value to set as the stable identifier version.
        variable (VariableType): The variable whose pseudonymization parameters are updated.

    Returns:
        str: The validated date in ISO format (`YYYY-MM-DD`).

    Raises:
        ValueError: If `field_value` is not a valid date.
        KeyError: If `encryption_algorithm_parameters` exists but no dictionary contains the snapshot date key.
    """
    validated_date: str
    try:
        validated_date = arrow.get(str(field_value)).format("YYYY-MM-DD")
    except arrow.parser.ParserError as e:
        error_message = ("Field_value %s is not a valid ISO date", field_value)
        raise ValueError(error_message) from e

    # Find the dict containing the snapshot date key
    if (
        variable
        and variable.pseudonymization
        and variable.pseudonymization.encryption_algorithm_parameters is not None
    ):
        for param_dict in variable.pseudonymization.encryption_algorithm_parameters:
            if constants.ENCRYPTION_PARAMETER_SNAPSHOT_DATE in param_dict:
                # Update only snapshotDate dict
                param_dict[constants.ENCRYPTION_PARAMETER_SNAPSHOT_DATE] = field_value
                break
        else:
            error_message = (
                "No parameter contains key %s",
                constants.ENCRYPTION_PARAMETER_SNAPSHOT_DATE,
            )
            raise KeyError(error_message)
    return validated_date


def parse_and_validate_pseudonymization_time(
    pseudo_date: str | datetime.datetime | None,
) -> datetime.datetime | None:
    """Parse and validate the given date.

    Validate that:
        - The date is in YYYY-MM-DD format

    Examples:
    >>> parse_and_validate_pseudonymization_time("2021-01-01")
    datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

    >>> parse_and_validate_pseudonymization_time("1990-01-01")
    datetime.datetime(1990, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

    >>> parse_and_validate_pseudonymization_time("1st January 2021")
    Traceback (most recent call last):
    ...
    ValueError: Validation error: Expected an ISO 8601-like string, but was given '1st January 2021'. Try passing in a format string to resolve this.

    >>> parse_and_validate_pseudonymization_time(None)
    None
    """
    if pseudo_date is None:
        return None
    parsed_date = None
    try:
        if pseudo_date:
            parsed_date = arrow.get(pseudo_date)
    except arrow.parser.ParserError as e:
        raise ValueError(VALIDATION_ERROR + str(e)) from e

    return parsed_date.astimezone(tz=datetime.UTC) if parsed_date else None


def update_selected_pseudonymization(
    variable: VariableType,
    new_algorithm: PseudonymizationAlgorithmsEnum,
) -> None:
    """Update the pseudonymization algorithm for a variable.

    This function replaces the variable's existing pseudonymization with a new one:
        - Removes the pseudonymization defined by the old algorithm.
        - Applies a new pseudonymization based on the newly selected algorithm.

    Args:
        variable (VariableType):
            The variable whose pseudonymization is being updated.
        new_algorithm (PseudonymizationAlgorithmsEnum):
            The newly selected pseudonymization algorithm.
    """
    if variable.short_name:
        state.metadata.remove_pseudonymization(variable.short_name)
        logger.debug(
            "Updating pseuonymization step 1: Remove pseudonymization for %s",
            variable.short_name,
        )
        apply_pseudonymization(variable, new_algorithm)
        logger.debug(
            "Updating pseuonymization step 2: Add new pseudonymization for %s.",
            variable.short_name,
        )
        logger.info(
            "Updating pseudonymization algorithm for %s to %s.",
            variable.short_name,
            new_algorithm,
        )


def delete_pseudonymization(variable: VariableType) -> None:
    """Remove pseudonymization for a Variable.."""
    state.metadata.remove_pseudonymization(
        variable.short_name,
    ) if variable.short_name else logger.debug(
        "Could not delete pseudonymization for %s", variable.short_name
    )
    logger.info("Removed pseudonymization for %s", variable.short_name)
