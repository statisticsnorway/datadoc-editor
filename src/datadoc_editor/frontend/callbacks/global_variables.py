"""Callback functions to do with global variables metadata."""

from __future__ import annotations

import logging
from typing import Any

from datadoc_editor import state
from datadoc_editor.frontend.fields.display_base import GlobalDropdownField
from datadoc_editor.frontend.fields.display_base import GlobalInputField
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_VARIABLES
from datadoc_editor.frontend.fields.display_variables import (
    GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME,
)

logger = logging.getLogger(__name__)


def _get_display_name_and_title(
    value_dict: dict, display_globals: list[GlobalDropdownField | GlobalInputField]
) -> list[tuple[str, str]]:
    """Return a list of (display_name, human-readable title) for the selected global values."""
    result = []

    for field in display_globals:
        if field.identifier not in value_dict:
            continue

        raw_value = value_dict[field.identifier]

        if isinstance(field, GlobalDropdownField):
            title = next(
                (
                    opt["title"]
                    for opt in field.options_getter()
                    if opt["id"] == raw_value
                ),
                raw_value,  # fallback
            )
        else:
            title = raw_value

        result.append((field.display_name, title))

    return result


def inherit_global_variable_values(
    global_values: dict, previous_data: dict | None
) -> dict:
    """Apply values from store_data to variables (actual write)."""
    previous_data = previous_data or {}
    logger.debug("Previous data %s", previous_data)
    display_values = _get_display_name_and_title(global_values, GLOBAL_VARIABLES)
    display_value_map = dict(display_values)
    affected_variables: dict[str, dict[str, Any]] = {}

    for field_name, display_name in GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME:
        raw_value = global_values.get(field_name)
        if raw_value is None:
            continue

        prev = previous_data.get(field_name, {})
        affected_variables[field_name] = {
            "display_name": display_name,
            "value": raw_value,
            "display_value": display_value_map.get(display_name, raw_value),
            "num_vars": prev.get("num_vars", 0),
            "vars_updated": prev.get("vars_updated", []).copy(),
        }
    for var in state.metadata.variables:
        if not var or not var.short_name:
            continue
        for field_name in affected_variables:  # noqa: PLC0206
            raw_value = affected_variables[field_name]["value"]
            current_value = getattr(var, field_name, None)
            if not current_value:
                setattr(var, field_name, raw_value)
                affected_variables[field_name]["num_vars"] += 1
                affected_variables[field_name]["vars_updated"].append(var.short_name)
    return affected_variables

def cancel_inherit_global_variable_values(store_data: dict) -> dict:
    """Remove all global added values."""
    logger.debug("Before cancel: %s", store_data)
    for field_name, field_data in store_data.items():
        for var in state.metadata.variables:
            if not var or not var.short_name:
                continue
            if var.short_name in field_data.get("vars_updated", []):
                setattr(var, field_name, None)
                logger.debug("values after cancel: %s", getattr(var, field_name))
    store_data.clear()
    logger.debug("After cancel: %s", store_data)
    return store_data


def remove_global_variable_all(
    store_data: dict,
    value_dict: dict,
    *,
    all_fields: bool,
) -> dict:
    """Remove one or all global variable values.

    - If all_fields=True: clear everything (button-triggered).
    - If all_fields=False: only remove invalid/empty values (field-triggered).
    """
    if all_fields:
        delete_fields = list(store_data.keys())  # remove all
    else:
        delete_fields = [
            field_id
            for field_id, val in value_dict.items()
            if val in ("", "-- Velg --", None)
        ]

    for field_id in delete_fields:
        # reset UI
        store_data.pop(field_id, None)
        value_dict.pop(field_id, None)

        # reset state (if metadata vars exist)
        for field_name, field_data in store_data.items():
            for var in state.metadata.variables:
                if not var or not var.short_name:
                    continue
                if var.short_name in field_data.get("vars_updated", []):
                    setattr(var, field_name, None)
                    logger.debug("values after cancel: %s", getattr(var, field_name))
    return store_data
