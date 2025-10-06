"""Tests for the global variables callbacks module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

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


@pytest.mark.usefixtures("_code_list_fake_classifications")
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


@dataclass
class GlobalTestScenario:
    """Data class global test scenarios."""

    global_values: dict
    expected_results: dict


global_scenarios = [
    GlobalTestScenario(
        global_values={
            "unit_type": "",
            "measurement_unit": "",
            "multiplication_factor": 2,
            "variable_role": "",
            "data_source": "",
            "temporality_type": "",
        },
        expected_results={
            "multiplication_factor": {
                "value": 2,
                "display_value": 2,
                "display_name": "Multiplikasjonsfaktor",
            },
        },
    ),
    GlobalTestScenario(
        global_values={
            "unit_type": "03",
            "measurement_unit": "",
            "multiplication_factor": None,
            "variable_role": "",
            "data_source": "",
            "temporality_type": "",
        },
        expected_results={
            "multiplication_factor": {
                "value": 2,
                "display_value": 2,
                "display_name": "Multiplikasjonsfaktor",
            },
            "unit_type": {
                "value": "03",
                "display_value": "Bolig",
                "display_name": "Enhetstype",
            },
        },
    ),
    GlobalTestScenario(
        global_values={
            "unit_type": "",
            "measurement_unit": "",
            "multiplication_factor": None,
            "variable_role": "ATTRIBUTE",
            "data_source": "",
            "temporality_type": "",
        },
        expected_results={
            "multiplication_factor": {
                "value": 2,
                "display_value": 2,
                "display_name": "Multiplikasjonsfaktor",
            },
            "unit_type": {
                "value": "03",
                "display_value": "Bolig",
                "display_name": "Enhetstype",
            },
            "variable_role": {
                "value": "ATTRIBUTE",
                "display_value": "ATTRIBUTT",
                "display_name": "Variabelens rolle",
            },
        },
    ),
]


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_inherit_globals_will_add_new_values(metadata: Datadoc):
    state.metadata = metadata

    # Count how many variables are missing certain fields before setting global values
    num_not_set = {
        "multiplication_factor": sum(
            1 for v in state.metadata.variables if not v.multiplication_factor
        ),
        "unit_type": sum(1 for v in state.metadata.variables if not v.unit_type),
        "variable_role": sum(
            1 for v in state.metadata.variables if not v.variable_role
        ),
        "measurement_unit": sum(
            1 for v in state.metadata.variables if not v.measurement_unit
        ),
        "data_source": sum(1 for v in state.metadata.variables if not v.data_source),
        "temporality_type": sum(
            1 for v in state.metadata.variables if not v.temporality_type
        ),
    }

    result = None
    for scenario in global_scenarios:
        result = inherit_global_variable_values(scenario.global_values, result)

        for field, expected in scenario.expected_results.items():
            field_result = result.get(field)
            if field_result is not None:
                for key, val in expected.items():
                    assert field_result[key] == val

                assert field_result["num_vars"] == num_not_set[field]
                assert len(field_result["vars_updated"]) == num_not_set[field]
            else:
                assert field_result is None


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_inherit_globals_has_values(metadata: Datadoc):
    state.metadata = metadata
    first_var_short_name = metadata.variables[0].short_name
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    assert variable.short_name
    variable.unit_type = "02"
    assert variable.unit_type == "02"
    not_set_unit_types = [
        var for var in metadata.variables if var.short_name != variable.short_name
    ]

    global_values = {
        "unit_type": "03",
        "measurement_unit": "",
        "multiplication_factor": 1,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }
    result = inherit_global_variable_values(global_values, None)
    unit_type_result = result.get("unit_type")
    assert unit_type_result is not None
    assert variable.unit_type == "02"
    assert unit_type_result["num_vars"] == len(not_set_unit_types)
    assert len(unit_type_result["vars_updated"]) == len(not_set_unit_types)
    assert variable.short_name not in not_set_unit_types
    for var in not_set_unit_types:
        assert var.unit_type == "03"


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
