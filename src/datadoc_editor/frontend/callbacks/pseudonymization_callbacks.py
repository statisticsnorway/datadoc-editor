"""Pseudonymization decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from dash import MATCH
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx
from dash import no_update

from datadoc_editor import state
from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.callbacks.variables import (
    accept_pseudo_variable_metadata_input,
)
from datadoc_editor.frontend.callbacks.variables import mutate_variable_pseudonymization
from datadoc_editor.frontend.callbacks.variables import populate_pseudo_workspace
from datadoc_editor.frontend.fields.display_base import PSEUDO_METADATA_INPUT

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc
    from dash import NoUpdate


logger = logging.getLogger(__name__)


def register_pseudonymization_callbacks(app: Dash) -> None:
    """Define and register callbacks for Pseudonymization."""

    @app.callback(
        Output({"type": "pseudo-field-container", "variable": MATCH}, "children"),
        Input({"type": "pseudonymization-dropdown", "variable": MATCH}, "value"),
        Input("save-button", "n_clicks"),
        State({"type": "pseudonymization-dropdown", "variable": MATCH}, "id"),
    )
    def callback_populate_pseudo_workspace(
        value,  # noqa: ANN001
        n_clicks: int,  # noqa: ARG001
        dropdown_id,  # noqa: ANN001
    ) -> dbc.Form | NoUpdate:
        """Dynamically create pseudonymization workspace.

        - The dropdown value updates the displayed pseudonymization fields immediately.
        - The Save button applies permanent changes (update or deletion) to the variable.
        """
        # Map dropdown value to enum if possible
        selected_algorithm = (
            PseudonymizationAlgorithmsEnum[value]
            if value and value in PseudonymizationAlgorithmsEnum.__members__
            else value
        )

        logger.debug("Selected algorithm: %s", selected_algorithm)
        variable = state.metadata.variables_lookup.get(dropdown_id["variable"])

        if variable is None:
            logger.info("Variable not found in lookup!")
            return no_update

        logger.debug("Triggered by: %s", ctx.triggered_id)

        # Perform changes when the user selects a new pseudonymization algorithm from the dropdown or clicks the save button
        if ctx.triggered_id in [dropdown_id, "save-button"]:
            mutate_variable_pseudonymization(variable, selected_algorithm)

        logger.debug(
            "Variable %s has pseudo info: %s",
            variable.short_name,
            variable.pseudonymization,
        )
        return populate_pseudo_workspace(variable, selected_algorithm)  # type: ignore[arg-type]

    @app.callback(
        Output(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "error",
        ),
        Output(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "errorMessage",
        ),
        Input(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "value",
        ),
        State(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "id",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_pseudo_variable_metadata_input(value, component_id):  # noqa: ANN202, ANN001
        if value is None or component_id is None:
            # Nothing to do if deselected or missing
            return False, ""
        variable_short_name = component_id["variable_short_name"]
        input_id = component_id["id"]
        logger.debug(
            "Callback triggered with value=%s, component_id=%s",
            value,
            component_id,
        )
        # Safely get variable from state
        variable = state.metadata.variables_lookup.get(variable_short_name)
        if not variable:
            logger.info("Variable not found: %s", variable_short_name)
            return False, "Variable not found."

        message = accept_pseudo_variable_metadata_input(
            value, variable_short_name, input_id
        )

        if not message:
            return False, ""

        return True, message
