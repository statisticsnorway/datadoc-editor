"""Tests for the global variables callbacks module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.global_variables import (
    inherit_global_variable_values,
)
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_VARIABLES

if TYPE_CHECKING:
    from dapla_metadata.datasets import Datadoc


def test_global():
    num_globals = 6
    assert len(GLOBAL_VARIABLES) == num_globals


def test_inherit_globals(metadata: Datadoc):
    state.metadata = metadata

    first_var_short_name = metadata.variables[0].short_name
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    variable.variable_role = None

    assert all(
        field is None
        for field in [
            variable.multiplication_factor,
            variable.variable_role,
            variable.temporality_type,
        ]
    )

    global_values = {
        "multiplication_factor": 2,
        "variable_role": "ATTRIBUTE",
        "temporality_type": "STATUS",
    }

    inherit_global_variable_values(global_values, None)
    expected_values = [2, "ATTRIBUTE", "STATUS"]

    assert variable.multiplication_factor == expected_values[0]
    assert variable.variable_role == expected_values[1]
    assert variable.temporality_type == expected_values[2]


def test_add_global_variables_will_add_to_state_value_if_value_was_none():
    pass


def test_add_global_variables_will_not_add_to_state_value_if_value():
    pass


def test_remove_one_from_global_variables_will_not_add_this_to_state():
    pass


def test_will_generate_global_variables_report_when_add_global_variables(
    metadata: Datadoc,
):
    state.metadata = metadata
    first_var_short_name = metadata.variables[0].short_name
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    variable.variable_role = None

    assert all(
        field is None
        for field in [
            variable.multiplication_factor,
            variable.variable_role,
            variable.temporality_type,
        ]
    )

    global_values = {
        "multiplication_factor": 2,
        "variable_role": "ATTRIBUTE",
        "temporality_type": "STATUS",
    }

    report = inherit_global_variable_values(global_values, None)
    assert report is not None
    assert isinstance(report, dict)
    expected_factor = 2
    assert report["multiplication_factor"]["display_value"] == expected_factor
    assert report["multiplication_factor"]["num_vars"] == len(
        report["multiplication_factor"]["vars_updated"]
    )
    assert report["variable_role"]["value"] == global_values["variable_role"]
    assert report["variable_role"]["display_value"] != global_values["variable_role"]


def test_generate_global_variables_report_has_correct_num_variables_and_updated_fields():
    pass


def test_remove_one_global_variable():
    pass


def test_reset_all_global_variables_will_remove_from_state_and_reset_fields():
    pass


def test_save_global_variables():
    pass


def test_add_global_variable_only_once():
    pass
