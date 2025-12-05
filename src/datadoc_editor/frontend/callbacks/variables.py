"""Callback functions to do with variables metadata."""

from __future__ import annotations

import contextlib
import datetime
import logging
import urllib.parse
from typing import TYPE_CHECKING
from typing import cast

from dapla_metadata.datasets import model

from datadoc_editor import state
from datadoc_editor.constants import PAPIS_ALGORITHM_ENCRYPTION
from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes
from datadoc_editor.frontend.callbacks.utils import PseudonymizationInputTypes
from datadoc_editor.frontend.callbacks.utils import apply_pseudonymization
from datadoc_editor.frontend.callbacks.utils import delete_pseudonymization
from datadoc_editor.frontend.callbacks.utils import find_existing_language_string
from datadoc_editor.frontend.callbacks.utils import map_dropdown_to_pseudo
from datadoc_editor.frontend.callbacks.utils import (
    map_selected_algorithm_to_pseudo_fields,
)
from datadoc_editor.frontend.callbacks.utils import parse_and_validate_dates
from datadoc_editor.frontend.callbacks.utils import (
    parse_and_validate_pseudonymization_time,
)
from datadoc_editor.frontend.callbacks.utils import update_selected_pseudonymization
from datadoc_editor.frontend.callbacks.utils import update_stable_identifier_version
from datadoc_editor.frontend.components.builders import build_edit_section
from datadoc_editor.frontend.components.builders import build_pseudo_field_section
from datadoc_editor.frontend.components.builders import build_ssb_accordion
from datadoc_editor.frontend.components.builders import build_variables_machine_section
from datadoc_editor.frontend.components.builders import (
    build_variables_pseudonymization_section,
)
from datadoc_editor.frontend.constants import DELETE_SELECTED
from datadoc_editor.frontend.constants import INVALID_DATE_ORDER
from datadoc_editor.frontend.constants import INVALID_VALUE
from datadoc_editor.frontend.constants import PSEUDONYMIZATION
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PseudoVariableIdentifiers,
)
from datadoc_editor.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc_editor.frontend.fields.display_variables import (
    MULTIPLE_LANGUAGE_VARIABLES_METADATA,
)
from datadoc_editor.frontend.fields.display_variables import (
    NON_EDITABLE_VARIABLES_METADATA,
)
from datadoc_editor.frontend.fields.display_variables import VARIABLES_METADATA_LEFT
from datadoc_editor.frontend.fields.display_variables import VARIABLES_METADATA_RIGHT
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc
    from dapla_metadata.datasets import model
    from dapla_metadata.datasets.utility.utils import VariableListType
    from dapla_metadata.datasets.utility.utils import VariableType
    from dash.development.base_component import Component

    from datadoc_editor.frontend.fields.display_base import MetadataUrnField


logger = logging.getLogger(__name__)


def populate_variables_workspace(
    variables: VariableListType,
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
                    [VARIABLES_METADATA_LEFT, VARIABLES_METADATA_RIGHT],  # type: ignore [list-item]
                    variable,
                ),
                build_variables_machine_section(
                    NON_EDITABLE_VARIABLES_METADATA,
                    "Maskingenerert",
                    variable,
                ),
                build_variables_pseudonymization_section(
                    PSEUDONYMIZATION,
                    variable,
                    map_dropdown_to_pseudo(variable),
                ),
            ],
        )
        for variable in variables
        if search_query in (variable.short_name or "")
    ]


def handle_multi_language_metadata(
    metadata_field: str,
    new_value: MetadataInputTypes | model.LanguageStringType,
    variable: VariableType,
    language: str,
) -> MetadataInputTypes | model.LanguageStringType:
    """Handle updates to fields which support multiple languages."""
    if new_value is None:
        # This edge case occurs when the user removes the text in an input field
        # We want to ensure we only remove the content for the current language,
        # not create a new blank object!
        return find_existing_language_string(
            variable,
            "",
            metadata_field,
            language,
        )

    if isinstance(new_value, str):
        return find_existing_language_string(
            variable,
            new_value,
            metadata_field,
            language,
        )

    return new_value


def accept_variable_metadata_input(
    value: MetadataInputTypes,
    variable_short_name: str,
    metadata_field: VariableIdentifiers,
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
    variable = get_variable_from_state(variable_short_name)
    try:
        if (
            metadata_field in MULTIPLE_LANGUAGE_VARIABLES_METADATA
            and language is not None
        ):
            new_value = handle_multi_language_metadata(
                metadata_field,
                value,
                variable,
                language,
            )
        elif value in ("", DELETE_SELECTED):
            # Allow clearing non-multiple-language text fields
            new_value = None
        elif metadata_field in [
            VariableIdentifiers.DEFINITION_URI,
            VariableIdentifiers.CLASSIFICATION_URI,
        ] and isinstance(value, str):
            new_value = cast(
                "MetadataUrnField",
                DISPLAY_VARIABLES[metadata_field],
            ).value_setter(value)
        else:
            new_value = value

        # Write the value to the variables structure
        setattr(
            variable,
            metadata_field,
            new_value,
        )
    except ValueError:
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


def accept_pseudo_variable_metadata_input(
    value: PseudonymizationInputTypes,
    variable_short_name: str,
    metadata_field: str,
) -> str | None:
    """Validate and save a pseudo-variable metadata field.

    Depending on the metadata field:
    - If `metadata_field` is 'pseudonymization_time', the input is parsed and validated as a date/time.
    - If `metadata_field` is 'stable_identifier_version', the value is validated as a date (or set to today by default)
        and `snapshotDate` is updated accordingly.
    - For all other fields, string values are stripped of whitespace.

    The function updates the corresponding field in the variable's pseudonymization metadata.

    Args:
        value (PseudonymizationInputTypes): The new value to set for the metadata field.
        variable_short_name (str): The short name of the variable whose metadata is updated.
        metadata_field (str): The metadata field to update.

    Returns:
        str | None: Returns an error message if validation fails, otherwise `None`.
    """
    try:
        parsed_value: PseudonymizationInputTypes = None
        variable = get_variable_from_state(variable_short_name)
        if variable:
            if (
                metadata_field == PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME
                and isinstance(value, (datetime.datetime, str))
            ):
                parsed_value = parse_and_validate_pseudonymization_time(value)
            elif metadata_field == PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION:
                if (
                    variable.pseudonymization
                    and variable.pseudonymization.encryption_algorithm
                    == PAPIS_ALGORITHM_ENCRYPTION
                ):
                    if value is None:
                        value = datetime.datetime.now(datetime.UTC).date().isoformat()
                    if isinstance(value, str):
                        value = value.strip()
                    parsed_value = update_stable_identifier_version(
                        value, get_variable_from_state(variable_short_name)
                    )
                else:
                    if isinstance(value, str):
                        value = value.strip()
                    parsed_value = value if value else None
            elif isinstance(value, str):
                parsed_value = value.strip() or None
            else:
                parsed_value = value or None
            setattr(
                get_variable_from_state(variable_short_name).pseudonymization,
                metadata_field,
                parsed_value,
            )
    except ValueError:
        logger.exception(
            "Validation failed for %s, %s, %s:",
            metadata_field,
            variable_short_name,
            value,
        )
        return INVALID_VALUE
    else:
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
    variable = get_variable_from_state(variable_short_name)

    try:
        (
            parsed_contains_data_from,
            parsed_contains_data_until,
        ) = parse_and_validate_dates(
            str(
                contains_data_from or variable.contains_data_from,
            ),
            str(
                contains_data_until or variable.contains_data_until,
            ),
        )

        # Save both values to the model if they pass validation.
        variable.contains_data_from = parsed_contains_data_from
        variable.contains_data_until = parsed_contains_data_until
    except ValueError as e:
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


def rerender_urn_field(
    value: MetadataInputTypes,
    variable_short_name: str,
    component_id: dict,
    field_id: VariableIdentifiers,
) -> list[Component]:
    """Render information for editing and viewing.

    - Update the Identifier value so that the user can modify it.
    - If there is a valid value, also show a link to the resource in the data catalog.

    Args:
        value (MetadataInputTypes): The vaue from user input in the frontend.
        variable_short_name (str): The short name of the variable being edited.
        component_id (dict): The ID dictionary of the field being edited.
        field_id (VariableIdentifiers): Which Metadata field is being edited.

    Raises:
        RuntimeError: When the variable being edited cannot be found in metadata.

    Returns:
        list[Component]: The updated field components to be rendered in the frontend.
    """
    with contextlib.suppress(ValueError):
        # Make sure the value actually gets set before we re-render.
        # We don't handle validation and error messages in this callback so we
        # just suppress the exception.
        accept_variable_metadata_input(
            value=value,
            variable_short_name=variable_short_name,
            metadata_field=field_id,
        )
    if variable := state.metadata.variables_lookup.get(variable_short_name):
        return (
            DISPLAY_VARIABLES[field_id]
            .render(
                component_id=component_id,
                metadata=variable,
            )
            .children
        )

    # If we get down here then something is very wrong indeed.
    msg = (
        f"Editing a variable which can't be found in metadata: '{variable_short_name}'"
    )
    raise RuntimeError(msg)


def validate_field_name(
    dataset_identifier: str,
) -> str | None:
    """Pair corresponding identifiers."""
    metadata_identifiers = {
        "temporality_type": VariableIdentifiers.TEMPORALITY_TYPE,
        "data_source": VariableIdentifiers.DATA_SOURCE,
        "contains_data_from": VariableIdentifiers.CONTAINS_DATA_FROM,
        "contains_data_until": VariableIdentifiers.CONTAINS_DATA_UNTIL,
    }
    return metadata_identifiers.get(dataset_identifier)


def validate_field_name_multilanguage(
    dataset_identifier: str,
) -> str | None:
    """Pair corresponding identifiers for multilanguage fields."""
    metadata_identifiers = {
        "population_description": VariableIdentifiers.POPULATION_DESCRIPTION,
    }
    return metadata_identifiers.get(dataset_identifier)


def set_variables_values_inherit_dataset_values(
    value: MetadataInputTypes | model.LanguageStringType,
    dataset_metadata_identifier: str,
) -> None:
    """Set variable value based on dataset value."""
    field_name = validate_field_name(dataset_metadata_identifier)
    if value is not None and field_name is not None:
        for v in state.metadata.variables:
            setattr(
                v,
                field_name,
                value,
            )


def set_variables_value_multilanguage_inherit_dataset_values(
    value: MetadataInputTypes | model.LanguageStringType,
    metadata_identifier: str,
    language: str,
) -> None:
    """Set variable multilanguage value based on dataset value."""
    field_name = validate_field_name_multilanguage(metadata_identifier)
    if value is not None and field_name is not None:
        for v in state.metadata.variables:
            update_value = handle_multi_language_metadata(
                field_name,
                value,
                v,
                language,
            )
            setattr(
                v,
                field_name,
                update_value,
            )


def set_variables_values_inherit_dataset_derived_date_values() -> None:
    """Set variable date values if variables date values are not set.

    Covers the case for inherit dataset date values where dates are derived from dataset path
    and must be set on file opening.
    """
    for v in state.metadata.variables:
        if v.contains_data_from is None:
            setattr(
                v,
                VariableIdentifiers.CONTAINS_DATA_FROM,
                state.metadata.dataset.contains_data_from,
            )
        if v.contains_data_until is None:
            setattr(
                v,
                VariableIdentifiers.CONTAINS_DATA_UNTIL,
                state.metadata.dataset.contains_data_until,
            )


def populate_pseudo_workspace(
    variable: VariableType,
    selected_algorithm: PseudonymizationAlgorithmsEnum | None,
) -> dbc.Form:
    """Build pseudonymization workspace for a variable.

    Infers or applies variable pseudonymization.
    Builds pseudonymization workspace dynamically based on selected pseudo algorithm.

    Args:
        variable (VariableType):
            The variable to build the pseudonymization workspace for.
        selected_algorithm (PseudonymizationAlgorithmsEnum | str | None):
            The pseudonymization algorithm selected by the user.
            If None and the variable already has pseudonymization, the algorithm
            is inferred from the existing state.

    Returns:
        dbc.Form | list:
            Pseudonymization fields based on selection if pseudonymization; otherwise, an empty list.
    """
    if not selected_algorithm and variable.pseudonymization:
        selected_algorithm = map_dropdown_to_pseudo(variable)

    if selected_algorithm and not variable.pseudonymization:
        apply_pseudonymization(variable, selected_algorithm)
        logger.info("Added pseudonymization for %s", variable.short_name)

    if variable.pseudonymization is None:
        logger.info(
            "No pseudonymization for %s, returning empty list", variable.short_name
        )
        return []

    return build_pseudo_field_section(
        map_selected_algorithm_to_pseudo_fields(selected_algorithm),
        "left",
        variable=variable,
        pseudonymization=variable.pseudonymization,
        field_id="pseudo",
    )


def mutate_variable_pseudonymization(
    variable: VariableType,
    selected_algorithm: PseudonymizationAlgorithmsEnum | str | None,
) -> None:
    """Updates or delete variable pseudonymization.

    Depending on the selected algorithm, this function will update the existing
    pseudonymization or delete it.

    Args:
        variable (model.Variable):
            The variable whose pseudonymization should be mutated.
        selected_algorithm (PseudonymizationAlgorithmsEnum | str | None):
            The pseudonymization algorithm selected by the user. If equal to
            "delete_selected", the pseudonymization is removed. If an algorithm is
            provided and differs from the inferred algorithm, the pseudonymization
            is updated accordingly.
    """
    if selected_algorithm == DELETE_SELECTED and variable.pseudonymization:
        delete_pseudonymization(variable)
        return

    if (
        isinstance(selected_algorithm, PseudonymizationAlgorithmsEnum)
        and variable.pseudonymization
    ):
        inferred_algorithm = map_dropdown_to_pseudo(variable)
        if inferred_algorithm and inferred_algorithm != selected_algorithm:
            update_selected_pseudonymization(variable, selected_algorithm)
        return


def get_variable_from_state(short_name: str | None) -> VariableType:
    """Use a variable's short name to retrieve the variable from the global state object.

    Args:
        short_name (str | None): The short name for the variable. Allows None in the type for compatibility with the optional model type.

    Raises:
        ValueError: If short_name is None.
        IndexError: If the short_name is not known.

    Returns:
        VariableType: The variable corresponding to the given short_name.
    """
    if short_name is None:
        msg = "Variable does not have a value for short_name!"
        raise ValueError(msg)
    return state.metadata.variables_lookup[urllib.parse.unquote(short_name)]
