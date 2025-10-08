"""Callback functions to do with global variables metadata."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datadoc_editor import state
from datadoc_editor.frontend.components.builders import AlertTypes
from datadoc_editor.frontend.components.builders import build_ssb_alert
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
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
    """Build an info Alert."""
    info_alert_list: list = []
    info_alert_list.extend(
        f"{field_data['display_name']}: {field_data['num_vars']} variabler oppdateres med: {field_data.get('display_value')}"
        for field_data in affected_variables.values()
    )
    return build_ssb_alert(
        alert_type=AlertTypes.INFO,
        title="Globale verdier",
        message="Oppdatert verdiene for:",
        link=None,
        alert_list=info_alert_list,
    )


def inherit_global_variable_values(
    global_values: dict, previous_data: dict | None
) -> dict:
    """Apply values from store_data to variables (actual write)."""
    previous_data = previous_data or {}

    display_values = _get_display_name_and_title(global_values, GLOBAL_VARIABLES)
    display_value_map = dict(display_values)
    affected_variables = previous_data.copy()

    for field_name, display_name in GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME:
        raw_value = global_values.get(field_name)
        if not raw_value:
            continue
        display_value = display_value_map.get(display_name, raw_value)
        #if field_name in affected_variables:
        #    continue
        # if not raw_value or raw_value == DROPDOWN_DESELECT_OPTION:
        #     continue
        if field_name in affected_variables:
            # Compare and update if global value changed
            prev_value = affected_variables[field_name].get("value")
            if prev_value != raw_value:
                affected_variables[field_name]["value"] = raw_value
                affected_variables[field_name]["display_value"] = display_value
                affected_variables[field_name]["vars_updated"] = []  # reset before reapplying
                affected_variables[field_name]["num_vars"] = 0
        else:
        #if field_name not in affected_variables:
            affected_variables[field_name] = {
                "display_name": display_name,
                "value": raw_value,
                "display_value": display_value_map.get(display_name, raw_value),
                "num_vars": 0,
                "vars_updated": [],
            }
    for var in state.metadata.variables:
        if not var or not var.short_name:
            continue
        for field_name, meta in affected_variables.items():
            raw_value = meta["value"]
            current_value = getattr(var, field_name, None)
            # Update the variable if it's None OR if global value changed
            if current_value != raw_value:
                setattr(var, field_name, raw_value)
                meta["num_vars"] += 1
                meta["vars_updated"].append(var.short_name)
            #if getattr(var, field_name, None) is None:
            #    setattr(var, field_name, raw_value)
            #    meta["num_vars"] += 1
            #    meta["vars_updated"].append(var.short_name)
#
    return affected_variables


def remove_global_variables(
    store_data: dict,
) -> dict:
    """Remove all global variable values added in session."""
    logger.debug("Resetting all global variables...")
    for field_name, field_data in store_data.items():
        for var in state.metadata.variables:
            if not var or not var.short_name:
                continue
            if var.short_name in field_data.get("vars_updated", []):
                setattr(var, field_name, None)

    return {}
