"""Tests for the global variables callbacks module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.variables import inherit_global_variable_values

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
    variable.variable_role = None
    assert variable is not None
    assert all(
        field is None
        for field in [
            variable.multiplication_factor,
            variable.variable_role,
            variable.temporality_type,
        ]
    )

    global_values = {
        "multiplication_factor": "2",
        "variable_role": "ATTRIBUTE",
        "temporality_type": "STATUS",
    }

    inherit_global_variable_values(global_values, None)
    expected_values = [2, "ATTRIBUTE", "STATUS"]

    assert variable.multiplication_factor == expected_values[0]
    assert variable.variable_role == expected_values[1]
    assert variable.temporality_type == expected_values[2]
