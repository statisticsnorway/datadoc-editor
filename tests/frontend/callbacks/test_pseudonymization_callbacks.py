"""Tests for the pseudonymization callbacks module."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import model

from datadoc_editor import constants
from datadoc_editor import enums
from datadoc_editor import state
from datadoc_editor.frontend.callbacks.utils import apply_pseudonymization
from datadoc_editor.frontend.callbacks.utils import update_selected_pseudonymization
from datadoc_editor.frontend.callbacks.variables import (
    accept_pseudo_variable_metadata_input,
)
from datadoc_editor.frontend.callbacks.variables import mutate_variable_pseudonymization
from datadoc_editor.frontend.callbacks.variables import populate_pseudo_workspace
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PseudoVariableIdentifiers,
)

if TYPE_CHECKING:
    from dapla_metadata.datasets import Datadoc


@pytest.mark.parametrize(
    ("metadata_field", "value", "expected_model_value"),
    [
        (
            PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME,
            "2024-12-31",
            datetime.datetime(
                2024,
                12,
                31,
                0,
                0,
                0,
                tzinfo=datetime.UTC,
            ),
        ),
        (
            PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME,
            "",
            None,
        ),
        (
            PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME,
            None,
            None,
        ),
        (
            PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION,
            "stable identifier ",
            "stable identifier",
        ),
        (
            PseudoVariableIdentifiers.STABLE_IDENTIFIER_TYPE,
            "",
            None,
        ),
        (
            PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM,
            "TINK-FPE",
            "TINK-FPE",
        ),
        (
            PseudoVariableIdentifiers.ENCRYPTION_KEY_REFERENCE,
            "SSB_GLOBAL_KEY_1",
            "SSB_GLOBAL_KEY_1",
        ),
    ],
)
def test_accept_pseudo_variable_metadata_input_valid(
    metadata: Datadoc,
    metadata_field: PseudoVariableIdentifiers,
    value: str | datetime.datetime | None,
    expected_model_value: Any,  # noqa: ANN401
):
    state.metadata = metadata
    first_var_short_name = metadata.variables[0].short_name
    metadata.add_pseudonymization(first_var_short_name)
    assert (
        accept_pseudo_variable_metadata_input(
            value,
            first_var_short_name,
            metadata_field=metadata_field.value,
        )
        is None
    )
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    assert (
        getattr(
            variable.pseudonymization,
            metadata_field.value,
        )
        == expected_model_value
    )


@dataclass
class PseudoCaseWorkspace:
    """Test cases Pseudonymization."""

    selected_algorithm: enums.PseudonymizationAlgorithmsEnum | None | str
    expected_workspace_type: dbc.Form | list
    expected_number_editable_inputs: int
    expected_identifiers_in_workspace: list | None
    expected_variable_pseudonymization: bool
    saved_pseudonymization: model.Pseudonymization | None = None
    expected_algorithm_parameters_length: int | None = None


@pytest.mark.parametrize(
    "case",
    [
        PseudoCaseWorkspace(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=1,
            expected_identifiers_in_workspace=["pseudonymization_time"],
            expected_variable_pseudonymization=True,
            expected_algorithm_parameters_length=2,
        ),
        PseudoCaseWorkspace(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=2,
            expected_identifiers_in_workspace=[
                "pseudonymization_time",
                "stable_identifier_version",
            ],
            expected_variable_pseudonymization=True,
            expected_algorithm_parameters_length=3,
        ),
        PseudoCaseWorkspace(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=1,
            expected_identifiers_in_workspace=["pseudonymization_time"],
            expected_variable_pseudonymization=True,
            expected_algorithm_parameters_length=1,
        ),
        PseudoCaseWorkspace(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.CUSTOM,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=5,
            expected_identifiers_in_workspace=["pseudonymization_time"],
            expected_variable_pseudonymization=True,
            expected_algorithm_parameters_length=None,
        ),
        PseudoCaseWorkspace(
            selected_algorithm=None,
            expected_workspace_type=list,
            expected_number_editable_inputs=0,
            expected_identifiers_in_workspace=None,
            expected_variable_pseudonymization=False,
        ),
        PseudoCaseWorkspace(
            selected_algorithm=None,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=1,
            expected_identifiers_in_workspace=["pseudonymization_time"],
            expected_variable_pseudonymization=True,
            saved_pseudonymization=model.Pseudonymization(
                encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION
            ),
        ),
    ],
    ids=[
        "PAPIS without stable ID",
        "PAPIS without stable ID",
        "DAEAD",
        "Custom",
        "No algorithm selected",
        "None",
    ],
)
def test_populate_pseudonymization_workspace(
    case,
    metadata: Datadoc,
):
    state.metadata = metadata
    first_var_short_name = metadata.variables[0].short_name
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    if case.saved_pseudonymization:
        variable.pseudonymization = case.saved_pseudonymization
    pseudonymization_workspace = populate_pseudo_workspace(
        variable, case.selected_algorithm
    )
    assert pseudonymization_workspace is not None
    assert isinstance(pseudonymization_workspace, case.expected_workspace_type)
    if case.expected_number_editable_inputs > 0:
        assert (
            len(pseudonymization_workspace.children)
            == case.expected_number_editable_inputs
        )
        all_ids = [child.id["id"] for child in pseudonymization_workspace.children]
        for ids in case.expected_identifiers_in_workspace:
            assert ids in all_ids
    if case.expected_variable_pseudonymization is True:
        assert variable.pseudonymization is not None
        if variable.pseudonymization.encryption_algorithm_parameters is not None:
            assert case.expected_algorithm_parameters_length == len(
                variable.pseudonymization.encryption_algorithm_parameters
            )
    else:
        assert variable.pseudonymization is None


@pytest.mark.parametrize(
    "case",
    [
        PseudoCaseWorkspace(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=1,
            expected_identifiers_in_workspace=["pseudonymization_time"],
            expected_variable_pseudonymization=True,
            saved_pseudonymization=model.Pseudonymization(
                encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
                encryption_key_reference=constants.PAPIS_ENCRYPTION_KEY_REFERENCE,
                encryption_algorithm_parameters=[
                    {
                        constants.ENCRYPTION_PARAMETER_KEY_ID: constants.PAPIS_ENCRYPTION_KEY_REFERENCE
                    },
                    {
                        constants.ENCRYPTION_PARAMETER_STRATEGY: constants.ENCRYPTION_PARAMETER_STRATEGY_SKIP
                    },
                ],
            ),
            expected_algorithm_parameters_length=1,
        ),
        PseudoCaseWorkspace(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=2,
            expected_identifiers_in_workspace=["pseudonymization_time"],
            expected_variable_pseudonymization=True,
            saved_pseudonymization=model.Pseudonymization(
                encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION,
                encryption_key_reference=constants.DAEAD_ENCRYPTION_KEY_REFERENCE,
                encryption_algorithm_parameters=[
                    {
                        constants.ENCRYPTION_PARAMETER_KEY_ID: constants.DAEAD_ENCRYPTION_KEY_REFERENCE
                    }
                ],
            ),
            expected_algorithm_parameters_length=3,
        ),
        PseudoCaseWorkspace(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.CUSTOM,
            expected_workspace_type=dbc.Form,
            expected_number_editable_inputs=5,
            expected_identifiers_in_workspace=["pseudonymization_time"],
            expected_variable_pseudonymization=True,
            saved_pseudonymization=model.Pseudonymization(
                encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION,
                pseudonymization_time=datetime.datetime(
                    2024, 12, 31, 0, 0, 0, tzinfo=datetime.UTC
                ),
                encryption_algorithm_parameters=[
                    {
                        constants.ENCRYPTION_PARAMETER_KEY_ID: constants.DAEAD_ENCRYPTION_KEY_REFERENCE
                    }
                ],
            ),
            expected_algorithm_parameters_length=0,
        ),
    ],
    ids=[
        "Change from PAPIS without stable ID to DAEAD",
        "Change from DAEAD to PAPIS with stable ID",
        "Change from DAEAD to CUSTOM",
    ],
)
def test_update_pseudonymization_algorithm(case, metadata: Datadoc):
    state.metadata = metadata
    first_var_short_name = metadata.variables[0].short_name
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    if case.saved_pseudonymization:
        variable.pseudonymization = case.saved_pseudonymization
    update_selected_pseudonymization(
        variable,
        case.saved_pseudonymization.encryption_algorithm,
        case.selected_algorithm,
    )
    if case.expected_variable_pseudonymization is True:
        assert variable.pseudonymization is not None
        assert (
            variable.pseudonymization.pseudonymization_time
            == case.saved_pseudonymization.pseudonymization_time
        )
        if variable.pseudonymization.encryption_algorithm_parameters is not None:
            assert case.expected_algorithm_parameters_length == len(
                variable.pseudonymization.encryption_algorithm_parameters
            )


def test_delete_pseudonymization(
    metadata: Datadoc,
):
    state.metadata = metadata
    first_var_short_name = metadata.variables[0].short_name
    variable = state.metadata.variables_lookup.get(first_var_short_name)
    assert variable is not None
    variable.pseudonymization = model.Pseudonymization(
        encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION
    )
    assert variable.pseudonymization.encryption_algorithm == "TINK-DAEAD"
    mutate_variable_pseudonymization(variable, constants.DELETE_SELECTED)
    assert variable.pseudonymization is None


@dataclass
class PseudoCase:
    """Test cases Pseudonymization."""

    selected_algorithm: enums.PseudonymizationAlgorithmsEnum | None
    expected_stable_type: str | None
    expected_encryption_algorithm: str | None
    expected_encryption_key_reference: str | None
    expected_algorithm_parameters: list | None
    saved_pseudonymization: model.Pseudonymization | None = None
    expected_pseudonymization_time: datetime.datetime | None = None


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID,
            expected_stable_type=None,
            expected_encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
            expected_encryption_key_reference=constants.PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.PAPIS_ENCRYPTION_KEY_REFERENCE
                },
                {
                    constants.ENCRYPTION_PARAMETER_STRATEGY: constants.ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID,
            expected_stable_type=constants.PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
            expected_encryption_key_reference=constants.PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.PAPIS_ENCRYPTION_KEY_REFERENCE
                },
                {
                    constants.ENCRYPTION_PARAMETER_STRATEGY: constants.ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
                {
                    constants.ENCRYPTION_PARAMETER_SNAPSHOT_DATE: datetime.datetime.now(
                        datetime.UTC
                    )
                    .date()
                    .isoformat()
                },
            ],
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA,
            expected_stable_type=None,
            expected_encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION,
            expected_encryption_key_reference=constants.DAEAD_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.DAEAD_ENCRYPTION_KEY_REFERENCE
                },
            ],
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.CUSTOM,
            expected_stable_type=None,
            expected_encryption_algorithm=None,
            expected_encryption_key_reference=None,
            expected_algorithm_parameters=None,
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID,
            expected_stable_type=None,
            expected_encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
            expected_encryption_key_reference=constants.PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.PAPIS_ENCRYPTION_KEY_REFERENCE
                },
                {
                    constants.ENCRYPTION_PARAMETER_STRATEGY: constants.ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            saved_pseudonymization=model.Pseudonymization(
                encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION,
                encryption_key_reference=constants.DAEAD_ENCRYPTION_KEY_REFERENCE,
                pseudonymization_time=datetime.datetime(
                    2021, 1, 1, 0, 0, tzinfo=datetime.UTC
                ),
            ),
            expected_pseudonymization_time=datetime.datetime(
                2021, 1, 1, 0, 0, tzinfo=datetime.UTC
            ),
        ),
    ],
    ids=[
        "Selected PAPIS without stable ID",
        "Selected PAPIS with stable ID",
        "Selected DAEAD",
        "Selected custom",
        "Reselect: from DAEAD to PAPIS without stable ID",
    ],
)
def test_apply_pseudonymization_based_on_selected_algorithm(case, metadata: Datadoc):
    state.metadata = metadata
    variable = state.metadata.variables_lookup["sykepenger"]
    apply_pseudonymization(
        variable,
        case.selected_algorithm,
        case.saved_pseudonymization,
    )
    assert variable.pseudonymization is not None
    assert (
        variable.pseudonymization.encryption_algorithm
        == case.expected_encryption_algorithm
    )
    assert variable.pseudonymization.stable_identifier_type == case.expected_stable_type

    assert (
        variable.pseudonymization.encryption_key_reference
        == case.expected_encryption_key_reference
    )
    assert (
        variable.pseudonymization.encryption_algorithm_parameters
        == case.expected_algorithm_parameters
    )
    assert variable.pseudonymization.stable_identifier_type == case.expected_stable_type
    assert (
        variable.pseudonymization.pseudonymization_time
        == case.expected_pseudonymization_time
    )
