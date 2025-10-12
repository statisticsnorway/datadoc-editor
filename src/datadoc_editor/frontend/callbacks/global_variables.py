"""Callback functions to do with global variables metadata."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datadoc_editor import state
from datadoc_editor.frontend.components.global_variables_builders import (
    build_ssb_info_alert,
)
from datadoc_editor.frontend.constants import DELETE_SELECTED
from datadoc_editor.frontend.constants import DESELECT
from datadoc_editor.frontend.constants import GLOBAL_INFO_ALERT_DELETE_TEXT
from datadoc_editor.frontend.constants import GLOBAL_INFO_ALERT_UPDATE_TEXT
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
        f"{fd['display_name']}: {GLOBAL_INFO_ALERT_DELETE_TEXT}"
        if fd.get("delete")
        else f"{fd['display_name']}: {fd.get('num_vars', 0)} {GLOBAL_INFO_ALERT_UPDATE_TEXT}: {fd.get('display_value')}"
        for fd in affected_variables.values()
    )
    return build_ssb_info_alert(
        title=GLOBALE_ALERT_TITLE,
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
    delete_selected = set()
    preserve_field = set()
    deselect_selected = {}

    for field_name, display_name in GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME:
        raw_value = global_values.get(field_name)

        if raw_value == "":
            raw_value = None

        previous_entry: dict | None = previous_data.get(field_name)

        if raw_value == DESELECT or (
            field_name == "multiplication_factor" and not raw_value
        ):
            if previous_entry:
                logger.debug("Deselecting %s", field_name)
                deselect_selected.update({field_name: previous_entry})
                continue
            raw_value = None

        previous_value = previous_entry.get("value") if previous_entry else None

        if not previous_entry and not raw_value:
            continue

        if raw_value in (DELETE_SELECTED, "0"):
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
    global_values: dict,
    previous_data: dict,
    display_value_map: dict[str, str]
) -> tuple[dict[str, dict], set[str], set[str], dict[str, dict]]:
    """Decide what to update, delete, deselect, or preserve."""
    affected_variables: dict[str, dict] = {}
    delete_selected: set[str] = set()
    preserve_field: set[str] = set()
    deselect_selected: dict[str, dict] = {}

    for field_name, display_name in GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME:
        raw_value = global_values.get(field_name) or None
        previous_entry = previous_data.get(field_name)
        previous_value = previous_entry.get("value") if previous_entry else None

        # Deselect
        if raw_value == DESELECT or (
            field_name == "multiplication_factor" and not raw_value
        ):
            if previous_entry:
                deselect_selected[field_name] = previous_entry
                continue
            raw_value = None

        # Skip if nothing to do
        if not previous_entry and not raw_value:
            continue

        # Delete
        if raw_value in (DELETE_SELECTED, "0"):
            affected_variables[field_name] = {
                "display_name": display_name,
                "delete": True,
                "vars_updated": previous_entry.get("vars_updated", []) if previous_entry else [],
            }
            delete_selected.add(field_name)
            continue

        # Preserve unchanged
        if previous_value == raw_value or (previous_entry and not raw_value):
            if previous_entry:
                affected_variables[field_name] = previous_entry
                preserve_field.add(field_name)
            continue

        # Changed value → new record
        display_value = display_value_map.get(display_name, raw_value)
        affected_variables[field_name] = {
            "display_name": display_name,
            "vars_updated": previous_entry.get("vars_updated", []) if previous_entry else [],
            "num_vars": 0,
            "delete": False,
            "value": raw_value,
            "display_value": display_value,
        }

    return affected_variables, delete_selected, preserve_field, deselect_selected

def _apply_global_updates_to_state(
    state,
    affected_variables: dict[str, dict],
    delete_selected: set[str],
    preserve_field: set[str],
    deselect_selected: dict[str, dict],
    previous_data: dict,
):
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

        # Apply updates / deletions
        for field_name, meta in affected_variables.items():
            if field_name in preserve_field:
                continue

            old_value = getattr(var, field_name) or None
            meta.setdefault("vars_updated", {})
            if field_name not in previous_data:
                meta["vars_updated"][var.short_name] = old_value

            for delete_field in delete_selected:
                setattr(var, delete_field, None)

            if not meta.get("delete"):
                setattr(var, field_name, meta["value"])
                meta["num_vars"] += 1
