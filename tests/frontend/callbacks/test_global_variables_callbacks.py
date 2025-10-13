# ruff: noqa: PLR2004
"""Tests for the global variables callbacks module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import enums

from datadoc_editor import state
from datadoc_editor.enums import TemporalityTypeType
from datadoc_editor.enums import VariableRole
from datadoc_editor.frontend.callbacks.global_variables import (
    generate_info_alert_report,
)
from datadoc_editor.frontend.callbacks.global_variables import (
    inherit_global_variable_values,
)
from datadoc_editor.frontend.constants import DELETE_SELECTED
from datadoc_editor.frontend.constants import DESELECT
from datadoc_editor.frontend.constants import GLOBAL_INFO_ALERT_DELETE_TEXT
from datadoc_editor.frontend.constants import GLOBAL_INFO_ALERT_UPDATE_TEXT
from datadoc_editor.frontend.constants import GLOBALE_ALERT_TITLE
from datadoc_editor.frontend.constants import MAGIC_DELETE_INSTRUCTION_STRING
from datadoc_editor.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    from dapla_metadata.datasets import Datadoc


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
                "display_name": DISPLAY_VARIABLES[
                    VariableIdentifiers.MULTIPLICATION_FACTOR
                ].display_name,
            },
        },
    ),
    GlobalTestScenario(
        global_values={
            "unit_type": "03",
            "measurement_unit": "",
            "multiplication_factor": 2,
            "variable_role": "",
            "data_source": "",
            "temporality_type": "",
        },
        expected_results={
            "unit_type": {
                "value": "03",
                "display_value": "Bolig",
                "display_name": DISPLAY_VARIABLES[
                    VariableIdentifiers.UNIT_TYPE
                ].display_name,
            },
            "multiplication_factor": {
                "value": 2,
                "display_value": 2,
                "display_name": DISPLAY_VARIABLES[
                    VariableIdentifiers.MULTIPLICATION_FACTOR
                ].display_name,
            },
        },
    ),
    GlobalTestScenario(
        global_values={
            "unit_type": "02",
            "measurement_unit": "",
            "multiplication_factor": 2,
            "variable_role": VariableRole.ATTRIBUTE.value,
            "data_source": "",
            "temporality_type": "",
        },
        expected_results={
            "unit_type": {
                "value": "02",
                "display_value": "Arbeidsulykke",
                "display_name": DISPLAY_VARIABLES[
                    VariableIdentifiers.UNIT_TYPE
                ].display_name,
            },
            "multiplication_factor": {
                "value": 2,
                "display_value": 2,
                "display_name": DISPLAY_VARIABLES[
                    VariableIdentifiers.MULTIPLICATION_FACTOR
                ].display_name,
            },
            "variable_role": {
                "value": "ATTRIBUTE",
                "display_value": VariableRole.ATTRIBUTE.get_value_for_language(
                    enums.SupportedLanguages.NORSK_BOKMÅL
                ),
                "display_name": DISPLAY_VARIABLES[
                    VariableIdentifiers.VARIABLE_ROLE
                ].display_name,
            },
        },
    ),
]


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_edit_globally_selected_values(metadata: Datadoc):
    state.metadata = metadata
    result = None
    for scenario in global_scenarios_add:
        result = inherit_global_variable_values(scenario.global_values, result)
        for field, expected in scenario.expected_results.items():
            field_result = result.get(field)
            if field_result is not None:
                assert field_result["num_vars"] == len(metadata.variables)
                assert len(field_result["vars_updated"]) == len(metadata.variables)
                for key, val in expected.items():
                    assert field_result[key] == val


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_globally_overwrite_existing_variable_values(metadata: Datadoc):
    state.metadata = metadata
    unit_type_value_before = "02"
    for var in metadata.variables:
        var.unit_type = unit_type_value_before
    multiplication_factor_before = 1
    data_source_before = "05"
    metadata.variables[1].multiplication_factor = multiplication_factor_before
    metadata.variables[1].data_source = data_source_before

    global_values = {
        "unit_type": "04",
        "measurement_unit": "",
        "multiplication_factor": 3,
        "variable_role": "",
        "data_source": "",
        "temporality_type": TemporalityTypeType.STATUS,
    }

    inherit_global_variable_values(global_values, None)

    for var in metadata.variables:
        assert var.unit_type != unit_type_value_before
        assert var.multiplication_factor == global_values["multiplication_factor"]
        assert var.temporality_type == TemporalityTypeType.STATUS.value
    assert metadata.variables[1].data_source == data_source_before


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_globally_delete_existing_variable_values(metadata: Datadoc):
    state.metadata = metadata
    unit_type_value_before = "02"
    for var in metadata.variables:
        var.unit_type = unit_type_value_before
    multiplication_factor_before = 1
    data_source_before = "05"
    metadata.variables[1].multiplication_factor = multiplication_factor_before
    metadata.variables[1].data_source = data_source_before

    global_values = {
        "unit_type": DELETE_SELECTED,
        "measurement_unit": "",
        "multiplication_factor": MAGIC_DELETE_INSTRUCTION_STRING,
        "variable_role": "",
        "data_source": "",
        "temporality_type": DELETE_SELECTED,
    }

    inherit_global_variable_values(global_values, None)

    for var in metadata.variables:
        assert var.unit_type is None
        assert var.multiplication_factor is None
        assert var.temporality_type is None
    assert metadata.variables[1].data_source == data_source_before


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_globally_deselect_selected_variable_values(metadata: Datadoc):
    state.metadata = metadata
    unit_type_value_before = "06"
    for var in metadata.variables:
        var.unit_type = unit_type_value_before

    global_values_select = {
        "unit_type": "02",
        "measurement_unit": "",
        "multiplication_factor": "3",
        "variable_role": "",
        "data_source": "",
        "temporality_type": TemporalityTypeType.STATUS,
    }

    global_values_deselect = {
        "unit_type": DESELECT,
        "measurement_unit": "",
        "multiplication_factor": "03",
        "variable_role": "",
        "data_source": "",
        "temporality_type": "STATUS",
    }

    first_select = inherit_global_variable_values(global_values_select, None)
    for var in metadata.variables:
        assert var.unit_type == "02"
        assert var.temporality_type == TemporalityTypeType.STATUS.value
    deselect = inherit_global_variable_values(global_values_deselect, first_select)
    assert first_select["unit_type"]["value"] == "02"
    for var in metadata.variables:
        assert var.unit_type != "02"
        assert var.temporality_type == TemporalityTypeType.STATUS.value
        assert var.multiplication_factor == 3
    assert "unit_type" not in deselect
    assert metadata.variables[1].unit_type == unit_type_value_before


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_globally_multiplication_factor(metadata: Datadoc):
    state.metadata = metadata
    multiplication_factor_before = 6
    for var in metadata.variables:
        var.multiplication_factor = multiplication_factor_before

    global_values_select = {
        "unit_type": "",
        "measurement_unit": "",
        "multiplication_factor": 3,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }

    global_values_deselect = {
        "unit_type": "",
        "measurement_unit": "",
        "multiplication_factor": "",
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }

    global_values_reselect = {
        "unit_type": "",
        "measurement_unit": "",
        "multiplication_factor": 2,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }

    global_values_unchanged = {
        "unit_type": "",
        "measurement_unit": "",
        "multiplication_factor": "2",
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }

    global_values_delete = {
        "unit_type": "",
        "measurement_unit": "",
        "multiplication_factor": 0,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "",
    }

    first_select = inherit_global_variable_values(global_values_select, None)
    for var in metadata.variables:
        assert var.multiplication_factor == 3
    deselect = inherit_global_variable_values(global_values_deselect, first_select)
    for var in metadata.variables:
        assert var.multiplication_factor == 6
    reselect = inherit_global_variable_values(global_values_reselect, deselect)
    for var in metadata.variables:
        assert var.multiplication_factor == 2
    unchanged = inherit_global_variable_values(global_values_unchanged, reselect)
    for var in metadata.variables:
        assert var.multiplication_factor == 2
    deleted = inherit_global_variable_values(global_values_delete, unchanged)
    assert "multiplication_factor" not in deleted


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_no_global_session_data_returns_empty_dict(metadata: Datadoc):
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
def test_reset_global_session_data(metadata: Datadoc):
    state.metadata = metadata

    global_values_1 = {
        "unit_type": "04",
        "measurement_unit": "",
        "multiplication_factor": 3,
        "variable_role": "",
        "data_source": "",
        "temporality_type": "STATUS",
    }

    global_values_2 = {
        "unit_type": DELETE_SELECTED,
        "measurement_unit": "",
        "multiplication_factor": "",
        "variable_role": "",
        "data_source": "",
        "temporality_type": DELETE_SELECTED,
    }
    add_global_variables = inherit_global_variable_values(global_values_1, None)
    assert add_global_variables, "add_global_variables should not be empty"
    reset_added_global_variables = inherit_global_variable_values(
        global_values_2, add_global_variables
    )
    for field in reset_added_global_variables.values():
        assert field["delete"] is True


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_generate_global_variables_report(metadata: Datadoc):
    state.metadata = metadata
    num_variables = len(metadata.variables)

    global_values = {
        "unit_type": "03",
        "multiplication_factor": 2,
        "variable_role": VariableRole.MEASURE,
    }
    added_global_variables = inherit_global_variable_values(global_values, None)
    generated_report = generate_info_alert_report(added_global_variables)
    assert isinstance(generated_report, dbc.Alert)
    assert generated_report.children[0].children == GLOBALE_ALERT_TITLE
    assert len(generated_report.children[3].children) == len(global_values)
    for report_item in generated_report.children[3].children[0]:
        assert num_variables in report_item
        assert global_values.get("variable_role") in report_item
        assert GLOBAL_INFO_ALERT_UPDATE_TEXT in report_item


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_generate_global_variables_report_no_global_values(metadata: Datadoc):
    state.metadata = metadata
    global_values = {
        "unit_type": "",
        "multiplication_factor": "",
        "variable_role": "",
    }
    added_global_variables = inherit_global_variable_values(global_values, None)
    generate_report = generate_info_alert_report(added_global_variables)
    assert isinstance(generate_report, dbc.Alert)
    assert generate_report.children[0].children == GLOBALE_ALERT_TITLE
    assert len(generate_report.children[3].children) == 0


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_generate_global_variables_report_delete_all(metadata: Datadoc):
    state.metadata = metadata
    for var in metadata.variables:
        var.multiplication_factor = 6

    global_values = {
        "multiplication_factor": MAGIC_DELETE_INSTRUCTION_STRING,
    }
    added_global_variables = inherit_global_variable_values(global_values, None)
    generated_report = generate_info_alert_report(added_global_variables)
    assert isinstance(generated_report, dbc.Alert)
    assert generated_report.children[0].children == GLOBALE_ALERT_TITLE
    for report_item in generated_report.children[3].children[0]:
        assert global_values.get("multiplication_factor") in report_item
        assert GLOBAL_INFO_ALERT_DELETE_TEXT in report_item
