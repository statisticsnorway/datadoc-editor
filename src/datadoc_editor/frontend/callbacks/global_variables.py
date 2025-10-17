"""Callback functions to do with global variables metadata."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any

from datadoc_editor import state
from datadoc_editor.frontend.components.builders import AlertTypes
from datadoc_editor.frontend.components.builders import build_ssb_alert
from datadoc_editor.frontend.constants import DELETE_SELECTED
from datadoc_editor.frontend.constants import DESELECT
from datadoc_editor.frontend.constants import GLOBAL_INFO_ALERT_DELETE_TEXT
from datadoc_editor.frontend.constants import GLOBAL_INFO_ALERT_UPDATE_TEXT
from datadoc_editor.frontend.constants import GLOBALE_ALERT_TITLE
from datadoc_editor.frontend.constants import MAGIC_DELETE_INSTRUCTION_STRING
from datadoc_editor.frontend.constants import MULTIPLICATION_FACTOR
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
        f"{fd['display_name']}: {GLOBAL_INFO_ALERT_DELETE_TEXT}"
        if fd.get("delete")
        else f"{fd['display_name']}: {fd.get('num_vars', 0)} {GLOBAL_INFO_ALERT_UPDATE_TEXT}: {fd.get('display_value')}"
        for fd in affected_variables.values()
    )
    return build_ssb_alert(
        alert_type=AlertTypes.INFO,
        title=GLOBALE_ALERT_TITLE,
        alert_list=info_alert_list,
        is_dissmissable=False,
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

    affected_variables: dict = {}

    preserve_field: set = set()
    deselect_selected: dict[str, Any] = {}
    delete_selected: set = set()

    preserve_field, deselect_selected, delete_selected = _build_affected_variables(
        affected_variables,
        global_values,
        previous_data,
    )

    # Update, delete or reset valus in state
    for var in state.metadata.variables:
        if not getattr(var, "short_name", None):
            continue

        # Deselect
        for field_name, data in deselect_selected.items():
            if data.get("delete"):
                data["delete"] = False
            for key, value in data["vars_updated"].items():
                if var.short_name == key:
                    new_value = (
                        int(value)
                        if field_name == "multiplication_factor" and value
                        else value
                    )
                    setattr(var, field_name, new_value)

        # Apply updates
        for field_name, meta in affected_variables.items():
            if field_name in preserve_field:
                continue

            # Get the old value before updating
            old_value = getattr(var, field_name) or None
            if not isinstance(meta.get("vars_updated"), dict):
                meta["vars_updated"] = {}
            previous_entry = previous_data.get(field_name)
            if not previous_entry:
                meta["vars_updated"][var.short_name] = old_value

            # Delete
            for delete_field in delete_selected:
                setattr(var, delete_field, None)

            if meta["delete"] is False:
                raw_value = meta["value"]
                setattr(var, field_name, raw_value)
                meta["num_vars"] += 1
    return affected_variables


def _build_affected_variables(
    affected_variables: dict,
    global_values: dict,
    previous_data: dict,
) -> tuple[set, dict, set]:
    """Determine which global variables are new, reselected, deselected, deleted, or preserved.

    Updates the tracking structures in place to reflect detected changes.
    Internal helper for `inherit_global_variable_values()`.
    """
    display_values = _get_display_name_and_title(global_values, GLOBAL_VARIABLES)
    display_value_map = dict(display_values)

    delete_selected: set = set()
    preserve_field: set = set()
    deselect_selected: dict[str, Any] = {}

    for field_name, display_name in GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME:
        raw_value = global_values.get(field_name)

        if raw_value == "":
            raw_value = None

        previous_entry: dict | None = previous_data.get(field_name)

        if raw_value == DESELECT or (
            field_name == MULTIPLICATION_FACTOR and not raw_value
        ):
            if previous_entry:
                logger.debug("Deselecting %s", field_name)
                deselect_selected.update({field_name: previous_entry})
                continue
            raw_value = None

        previous_value = previous_entry.get("value") if previous_entry else None

        if not previous_entry and not raw_value:
            continue

        if raw_value in (DELETE_SELECTED, MAGIC_DELETE_INSTRUCTION_STRING):
            logger.debug("Delete or 0 %s %s", field_name, raw_value)
            previous_vars_updated = []
            if previous_entry:
                previous_vars_updated = previous_entry.get("vars_updated", [])
            affected_variables[field_name] = {
                "display_name": display_name,
                "delete": True,
                "vars_updated": previous_vars_updated,
            }
            delete_selected.add(field_name)
            continue

        display_value = display_value_map.get(display_name, raw_value)

        if previous_value == raw_value or (previous_entry and not raw_value):
            if previous_entry is not None:
                affected_variables[field_name] = previous_entry
                preserve_field.add(field_name)
                continue
        else:
            previous_vars_updated = []
            if previous_entry:
                previous_vars_updated = previous_entry.get("vars_updated", [])
            affected_variables[field_name] = {
                "display_name": display_name,
                "vars_updated": previous_vars_updated,
                "num_vars": 0,
                "delete": False,
                "value": raw_value,
                "display_value": display_value,
            }
    return preserve_field, deselect_selected, delete_selected
