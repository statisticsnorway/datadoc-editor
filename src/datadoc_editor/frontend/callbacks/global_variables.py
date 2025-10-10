"""Callback functions to do with global variables metadata."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datadoc_editor import state
from datadoc_editor.constants import DELETE_SELECTED
from datadoc_editor.frontend.components.global_variables_builders import (
    build_ssb_info_alert,
)
from datadoc_editor.frontend.constants import GLOBALE_ALERT_MESSAGE
from datadoc_editor.frontend.constants import GLOBALE_ALERT_TITLE
from datadoc_editor.frontend.fields.display_base import FieldTypes
from datadoc_editor.frontend.fields.display_base import MetadataDropdownField
from datadoc_editor.frontend.fields.display_variables import (
    GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME,
)
from datadoc_editor.frontend.fields.display_variables import GLOBAL_VARIABLES

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)


def _get_display_name_and_title(
    value_dict: dict, display_globals: list[FieldTypes]
) -> list[tuple[str, str]]:
    """Return a list of (display_name, human-readable title) for the selected global values."""
    result = []

    for field in display_globals:
        if field.identifier not in value_dict:
            continue

        raw_value = value_dict[field.identifier]

        if isinstance(field, MetadataDropdownField):
            title = next(
                (
                    opt["title"]
                    for opt in field.options_getter()
                    if opt["id"] == raw_value
                ),
                raw_value,
            )
        else:
            title = raw_value

        result.append((field.display_name, title))

    return result


def generate_info_alert_report(affected_variables: dict) -> dbc.Alert:
    """Create an informational alert summarizing updated global variables.

    Args:
        affected_variables (dict):
            A mapping of variable identifiers registered in global variables section.

    Returns:
        dbc.Alert:
            A Dash Bootstrap Components alert element displaying the summary of updates.
    """
    info_alert_list: list = []
    info_alert_list.extend(
        f"{field_data['display_name']}: {field_data['num_vars']} variabler oppdateres med: {field_data.get('display_value')}"
        for field_data in affected_variables.values()
    )
    return build_ssb_info_alert(
        title=GLOBALE_ALERT_TITLE,
        message=GLOBALE_ALERT_MESSAGE,
        alert_list=info_alert_list,
    )


def inherit_global_variable_values(
    global_values: dict, previous_data: dict | None
) -> dict:
    """Apply global edits to all variables simultaneously.

    Updates, resets, or removes variable values across all variables based on
    user selections, while preserving unchanged fields. This allows setting
    the same value for multiple variables simultaneously.

    Args:
        global_values (dict): The newly selected or edited global variable values.
        previous_data (dict | None): Previously stored variable metadata from the session.

    Returns:
        dict: All affected variables, including display names, updated values,
            number of variables updated, and which variables were modified.
    """
    previous_data = previous_data or {}

    display_values = _get_display_name_and_title(global_values, GLOBAL_VARIABLES)
    display_value_map = dict(display_values)

    affected_variables = {}
    remove_deselected = set()
    preserved_field = set()

    for field_name, display_name in GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME:
        raw_value = global_values.get(field_name)
        if raw_value == "":
            raw_value = None
        previous_entry = previous_data.get(field_name)
        previous_value = previous_entry.get("value") if previous_entry else None

        if not previous_entry and (not raw_value or raw_value == DELETE_SELECTED):
            continue

        if field_name == "multiplication_factor" and raw_value == "":
            raw_value = 0

        if raw_value in (DELETE_SELECTED, 0):
            remove_deselected.add(field_name)
            continue

        display_value = display_value_map.get(display_name, raw_value)
        affected_variables[field_name] = (
            previous_entry.copy()
            if previous_entry
            else {
                "display_name": display_name,
                "vars_updated": [],
                "num_vars": 0,
            }
        )

        if previous_value == raw_value:
            preserved_field.add(field_name)
        else:
            affected_variables[field_name].update(
                {
                    "value": raw_value,
                    "display_value": display_value,
                    "vars_updated": [],
                    "num_vars": 0,
                }
            )
    # Update all variables in state
    for var in state.metadata.variables:
        if not getattr(var, "short_name", None):
            continue

        # Remove previously added value
        for field_name in remove_deselected:
            setattr(var, field_name, None)

        # Apply updates
        for field_name, meta in affected_variables.items():
            if field_name in preserved_field:
                continue
            raw_value = meta["value"]
            setattr(var, field_name, raw_value)
            meta["num_vars"] += 1
            meta["vars_updated"].append(var.short_name)

    return {k: v for k, v in affected_variables.items() if v.get("value") is not None}
