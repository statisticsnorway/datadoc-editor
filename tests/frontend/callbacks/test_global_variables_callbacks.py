"""Tests for the global variables callbacks module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import pytest

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.global_variables import (
    generate_info_alert_report,
)
from datadoc_editor.frontend.callbacks.global_variables import (
    inherit_global_variable_values,
)
from datadoc_editor.frontend.callbacks.global_variables import remove_global_variables
from datadoc_editor.frontend.constants import GLOBAL_HEADER

if TYPE_CHECKING:
    from dapla_metadata.datasets import Datadoc


def _num_not_set(variables: list) -> dict:
    """Count variable fields with no value."""
    return {
        "multiplication_factor": sum(
            1 for v in variables if not v.multiplication_factor
        ),
        "unit_type": sum(1 for v in state.metadata.variables if not v.unit_type),
        "variable_role": sum(1 for v in variables if not v.variable_role),
        "measurement_unit": sum(1 for v in variables if not v.measurement_unit),
        "data_source": sum(1 for v in variables if not v.data_source),
        "temporality_type": sum(1 for v in variables if not v.temporality_type),
    }


@dataclass
class GlobalTestScenario:
    """Data class global test scenarios."""

    global_values: dict
    expected_results: dict


global_scenarios_add = [
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
def test_inherit_globals_increments_correct(metadata: Datadoc):
    state.metadata = metadata

    num_not_set_before = _num_not_set(state.metadata.variables)
    result = None
    for scenario in global_scenarios_add:
        result = inherit_global_variable_values(scenario.global_values, result)

        for field, expected in scenario.expected_results.items():
            field_result = result.get(field)
            if field_result is not None:
                for key, val in expected.items():
                    assert field_result[key] == val

                assert field_result["num_vars"] == num_not_set_before[field]
                assert len(field_result["vars_updated"]) == num_not_set_before[field]
            else:
                assert field_result is None


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_inherit_globals_no_values(metadata: Datadoc):
    state.metadata = metadata
    global_values = {
        "unit_type": "",
        "measurement_unit": "",
        "multiplication_factor": 0,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }
    result = inherit_global_variable_values(global_values, None)
    assert result == {}


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_inherit_globals_will_not_change_if_value(metadata: Datadoc):
    state.metadata = metadata
    first_var_short_name = metadata.variables[0].short_name
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    variable.unit_type = "02"
    assert variable.unit_type == "02"
    assert variable.multiplication_factor is None

    global_values = {
        "unit_type": "03",
        "multiplication_factor": 2,
    }

    inherit_global_variable_values(global_values, None)
    assert variable.multiplication_factor == global_values.get("multiplication_factor")
    assert variable.unit_type != global_values.get("unit_type")


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_reset_added_variables(metadata: Datadoc):
    state.metadata = metadata
    assert metadata.variables
    num_not_set_before = _num_not_set(state.metadata.variables)

    global_values = {
        "unit_type": "03",
        "measurement_unit": "01",
        "multiplication_factor": 1,
        "variable_role": "IDENTIFIER",
        "data_source": "05",
        "temporality_type": "STATUS",
    }
    result_add_global_variables = inherit_global_variable_values(global_values, None)
    num_not_set_after_inherit = _num_not_set(state.metadata.variables)

    for key in num_not_set_after_inherit:
        assert num_not_set_after_inherit.get(key) == 0

    remove_global_variables(result_add_global_variables)
    num_not_set_after_reset = _num_not_set(state.metadata.variables)

    for key in num_not_set_before:
        assert num_not_set_before.get(key) == num_not_set_after_reset.get(key)


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_generate_global_variables_report(metadata: Datadoc):
    state.metadata = metadata
    global_values = {
        "unit_type": "03",
        "multiplication_factor": 2,
        "variable_role": "ATTRIBUTE",
    }
    added_global_variables = inherit_global_variable_values(global_values, None)
    generate_report = generate_info_alert_report(added_global_variables)
    assert isinstance(generate_report, dbc.Alert)
    assert generate_report.children[0].children == GLOBAL_HEADER
    assert len(generate_report.children[3].children) == len(global_values)


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_generate_global_variables_report_no_result(metadata: Datadoc):
    state.metadata = metadata
    global_values = {
        "unit_type": "",
        "multiplication_factor": 0,
        "variable_role": "",
    }
    added_global_variables = inherit_global_variable_values(global_values, None)
    generate_report = generate_info_alert_report(added_global_variables)
    assert isinstance(generate_report, dbc.Alert)
    assert generate_report.children[0].children == GLOBAL_HEADER
    assert len(generate_report.children[3].children) == 0


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_add_and_reset_before_save(metadata: Datadoc):
    state.metadata = metadata
    assert metadata.variables
    global_values = {
        "unit_type": "03",
        "measurement_unit": "01",
        "multiplication_factor": 1,
        "variable_role": "IDENTIFIER",
        "data_source": "05",
        "temporality_type": "STATUS",
    }
    global_values_again = {
        "unit_type": "02",
    }
    result_add_global_variables = inherit_global_variable_values(global_values, None)
    reset = remove_global_variables(result_add_global_variables)
    assert reset == {}
    result_add_again = inherit_global_variable_values(global_values_again, reset)
    assert result_add_again["unit_type"]["value"] == "02"


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_inherit_globals_can_add_new_after_reset(metadata: Datadoc):
    state.metadata = metadata

    global_values_first = {
        "unit_type": "",
        "measurement_unit": "",
        "multiplication_factor": 2,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }
    global_values_second = {
        "unit_type": "03",
        "measurement_unit": "",
        "multiplication_factor": 1,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }
    first_result = inherit_global_variable_values(global_values_first, None)
    reset = remove_global_variables(first_result)
    second_result = inherit_global_variable_values(global_values_second, reset)
    first_multiplication_factor = first_result.get("multiplication_factor")
    second_multiplication_factor = second_result.get("multiplication_factor")
    unit_type = second_result.get("unit_type")
    assert first_multiplication_factor is not None
    assert second_multiplication_factor is not None
    assert unit_type is not None
    assert first_multiplication_factor.get("value") != second_multiplication_factor.get(
        "value"
    )
    assert unit_type.get("value") == "03"
