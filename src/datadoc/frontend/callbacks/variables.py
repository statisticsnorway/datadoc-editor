"""Callback functions to do with variables metadata."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import ValidationError

from datadoc import state
from datadoc.frontend.callbacks.utils import MetadataInputTypes
from datadoc.frontend.callbacks.utils import find_existing_language_string
from datadoc.frontend.callbacks.utils import parse_and_validate_dates
from datadoc.frontend.components.builders import build_edit_section
from datadoc.frontend.components.builders import build_ssb_accordion
from datadoc.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc.frontend.fields.display_variables import (
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
)
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA
from datadoc.frontend.fields.display_variables import VariableIdentifiers
from datadoc.frontend.text import INVALID_DATE_ORDER
from datadoc.frontend.text import INVALID_VALUE

if TYPE_CHECKING:
    from datadoc_model import model
    from datadoc_model.model import LanguageStringType


logger = logging.getLogger(__name__)


def populate_variables_workspace(
    variables: list[model.Variable],
    search_query: str,
    dataset_opened_counter: int,
) -> list:
    """Create variable workspace with accordions for variables.

    Allows for filtering which variables are displayed via the search box.
    """
    return [
        build_ssb_accordion(
            variable.short_name or "",
            {
                "type": "variables-accordion",
                "id": f"{variable.short_name}-{dataset_opened_counter}",  # Insert language into the ID to invalidate browser caches
            },
            variable.short_name or "",
            children=[
                build_edit_section(
                    OBLIGATORY_VARIABLES_METADATA,
                    "Obligatorisk",
                    variable,
                ),
                build_edit_section(
                    OPTIONAL_VARIABLES_METADATA,
                    "Anbefalt",
                    variable,
                ),
            ],
        )
        for variable in variables
        if search_query in (variable.short_name or "")
    ]


def handle_multi_language_metadata(
    metadata_field: str,
    new_value: MetadataInputTypes | LanguageStringType,
    updated_row_id: str,
    language: str,
) -> MetadataInputTypes | LanguageStringType:
    """Handle updates to fields which support multiple languages."""
    if new_value is None:
        # This edge case occurs when the user removes the text in an input field
        # We want to ensure we only remove the content for the current language,
        # not create a new blank object!
        return find_existing_language_string(
            state.metadata.variables_lookup[updated_row_id],
            "",
            metadata_field,
            language,
        )

    if isinstance(new_value, str):
        return find_existing_language_string(
            state.metadata.variables_lookup[updated_row_id],
            new_value,
            metadata_field,
            language,
        )

    return new_value


def accept_variable_metadata_input(
    value: MetadataInputTypes,
    variable_short_name: str,
    metadata_field: str,
    language: str | None = None,
) -> str | None:
    """Validate and save the value when variable metadata is updated.

    Returns an error message if an exception was raised, otherwise returns None.
    """
    logger.debug(
        "Updating %s, %s with %s",
        metadata_field,
        variable_short_name,
        value,
    )
    try:
        if (
            metadata_field in MULTIPLE_LANGUAGE_VARIABLES_METADATA
            and language is not None
        ):
            new_value = handle_multi_language_metadata(
                metadata_field,
                value,
                variable_short_name,
                language,
            )
        elif value == "":
            # Allow clearing non-multiple-language text fields
            new_value = None
        else:
            new_value = value

        # Write the value to the variables structure
        setattr(
            state.metadata.variables_lookup[variable_short_name],
            metadata_field,
            new_value,
        )
    except (ValidationError, ValueError):
        logger.exception(
            "Validation failed for %s, %s, %s:",
            metadata_field,
            variable_short_name,
            value,
        )
        return INVALID_VALUE
    else:
        if value == "":
            value = None
        logger.info(
            "Updated %s: %s with value '%s'",
            variable_short_name,
            metadata_field,
            value,
        )
        return None


def accept_variable_metadata_date_input(
    variable_identifier: VariableIdentifiers,
    variable_short_name: str,
    contains_data_from: str,
    contains_data_until: str,
) -> tuple[bool, str, bool, str]:
    """Validate and save date range inputs."""
    message = ""

    try:
        (
            parsed_contains_data_from,
            parsed_contains_data_until,
        ) = parse_and_validate_dates(
            str(
                contains_data_from
                or state.metadata.variables_lookup[
                    variable_short_name
                ].contains_data_from,
            ),
            str(
                contains_data_until
                or state.metadata.variables_lookup[
                    variable_short_name
                ].contains_data_until,
            ),
        )

        # Save both values to the model if they pass validation.
        state.metadata.variables_lookup[
            variable_short_name
        ].contains_data_from = parsed_contains_data_from
        state.metadata.variables_lookup[
            variable_short_name
        ].contains_data_until = parsed_contains_data_until
    except (ValidationError, ValueError) as e:
        logger.exception(
            "Validation failed for %s, %s, %s: %s, %s: %s",
            variable_identifier,
            variable_short_name,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )
        message = str(e)
    else:
        logger.debug(
            "Successfully updated %s, %s, %s: %s, %s: %s",
            variable_identifier,
            variable_short_name,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )

    no_error = (False, "")
    if not message:
        # No error to display.
        return no_error + no_error

    error = (
        True,
        INVALID_DATE_ORDER.format(
            contains_data_from_display_name=DISPLAY_VARIABLES[
                VariableIdentifiers.CONTAINS_DATA_FROM
            ].display_name,
            contains_data_until_display_name=DISPLAY_VARIABLES[
                VariableIdentifiers.CONTAINS_DATA_UNTIL
            ].display_name,
        ),
    )
    return (
        error + no_error
        if variable_identifier == VariableIdentifiers.CONTAINS_DATA_FROM
        else no_error + error
    )


def set_dataset_values_variables() -> None:
    """Test method for setting variables value based on dataset value."""
    update_value: str | LanguageStringType
    for val in state.metadata.variables:
        if state.metadata.dataset.temporality_type is not None:
            update_value = state.metadata.dataset.temporality_type
            setattr(
                state.metadata.variables_lookup[val.short_name],
                VariableIdentifiers.TEMPORALITY_TYPE,
                update_value,
            )
        if state.metadata.dataset.data_source is not None:
            update_value = state.metadata.dataset.data_source
            setattr(
                state.metadata.variables_lookup[val.short_name],
                VariableIdentifiers.DATA_SOURCE,
                update_value,
            )
        if state.metadata.dataset.population_description is not None:
            update_value = state.metadata.dataset.population_description
            setattr(
                state.metadata.variables_lookup[val.short_name],
                VariableIdentifiers.POPULATION_DESCRIPTION,
                update_value,
            )
