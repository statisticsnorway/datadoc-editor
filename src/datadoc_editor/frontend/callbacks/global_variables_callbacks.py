"""Global variables decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions in 'global_variables', to enable unit testing.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import dash
from dash import ALL
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.global_variables import (
    generate_info_alert_report,
)
from datadoc_editor.frontend.callbacks.global_variables import (
    inherit_global_variable_values,
)
from datadoc_editor.frontend.callbacks.global_variables import remove_global_variables
from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_edit_section,
)
from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_ssb_accordion,
)
from datadoc_editor.frontend.components.identifiers import ADD_GLOBAL_VARIABLES_BUTTON
from datadoc_editor.frontend.components.identifiers import GLOBAL_ADDED_VARIABLES_STORE
from datadoc_editor.frontend.components.identifiers import GLOBAL_INFO_ALERTS_OUTPUT
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_ID
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_VALUES_STORE
from datadoc_editor.frontend.components.identifiers import RESET_GLOBAL_VARIABLES_BUTTON
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_HEADER
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_VARIABLES
from datadoc_editor.frontend.fields.display_global_variables import (
    GLOBAL_VARIABLES_INPUT,
)

if TYPE_CHECKING:
    import ssb_dash_components as ssb

logger = logging.getLogger(__name__)


def register_global_variables_callbacks(app: Dash) -> None:
    """Define and register callbacks for global variables values."""

    @app.callback(
        Output(GLOBAL_VARIABLES_ID, "children"),
        Input("dataset-opened-counter", "data"),
        Input(GLOBAL_VARIABLES_VALUES_STORE, "data"),
    )
    def callback_populate_variables_globals_section(
        dataset_opened_counter: int,  # noqa: ARG001
        store_data,  # noqa: ANN001
    ) -> None | ssb.Accordion:
        """Populating global variables section."""
        if state.metadata.variables and len(state.metadata.variables) > 0:
            return build_global_ssb_accordion(
                header=GLOBAL_HEADER,
                key={"id": "global_id", "type": "accordion"},
                children=build_global_edit_section(GLOBAL_VARIABLES, store_data),
            )
        return None

    @app.callback(
        Output(GLOBAL_VARIABLES_VALUES_STORE, "data"),
        Input({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "value"),
        State({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def select_global_values(values, ids) -> dash.NoUpdate | dict:  # noqa: ANN001
        """Store selected fields and values in memory."""
        return dict(zip([i["id"] for i in ids], values, strict=False))

    @app.callback(
        Output(GLOBAL_ADDED_VARIABLES_STORE, "data"),
        Output(GLOBAL_INFO_ALERTS_OUTPUT, "children"),
        Input(ADD_GLOBAL_VARIABLES_BUTTON, "n_clicks"),
        State(GLOBAL_ADDED_VARIABLES_STORE, "data"),
        State(GLOBAL_VARIABLES_VALUES_STORE, "data"),
        prevent_initial_call=True,
    )
    def add_global_variables(
        n_clicks: int,
        added_variables_store: dict,
        selected_values: dict,
    ) -> tuple | dash.NoUpdate:
        """Add selected global variables.

        Update metadata state with selected values.
        Store result in memory and return info report.
        """
        if ctx.triggered_id == ADD_GLOBAL_VARIABLES_BUTTON and n_clicks:
            affected_variables = inherit_global_variable_values(
                selected_values, added_variables_store
            )
            added_variables_store = {
                **(added_variables_store or {}),
                **affected_variables,
            }
            logger.debug("Store %s", added_variables_store)
            return added_variables_store, generate_info_alert_report(
                added_variables_store
            )
        return dash.no_update, dash.no_update

    @app.callback(
        Output(GLOBAL_INFO_ALERTS_OUTPUT, "children", allow_duplicate=True),
        Output({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "value"),
        Output(GLOBAL_ADDED_VARIABLES_STORE, "data", allow_duplicate=True),
        Input(RESET_GLOBAL_VARIABLES_BUTTON, "n_clicks"),
        State(GLOBAL_ADDED_VARIABLES_STORE, "data"),
        State({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def reset_global_variables(  # noqa: ANN202
        n_clicks: int,
        added_variables_data: dict,
        component_ids,  # noqa: ANN001
    ):
        """Reset metadata state and update input fields.

        Remove added values from metadata state, and reset input fields.
        """
        if not n_clicks:
            return dash.no_update
        if ctx.triggered_id == "reset-global-variables-button" and n_clicks:
            new_store = remove_global_variables(added_variables_data)
            return None, [""] * len(component_ids), new_store
        return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output(
            {"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "value", allow_duplicate=True
        ),
        Output(GLOBAL_ADDED_VARIABLES_STORE, "data", allow_duplicate=True),
        Output(GLOBAL_INFO_ALERTS_OUTPUT, "children", allow_duplicate=True),
        Input("save-button", "n_clicks"),
        State({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def reset_global_variables_ui_on_save(
        n_clicks: int,
        component_ids,  # noqa: ANN001
    ) -> tuple:
        """Reset when data is saved to file.

        Reset input fields, reset local store data and reset info alert section.
        """
        if ctx.triggered_id == "save-button" and n_clicks:
            return [""] * len(component_ids), {}, None
        return dash.no_update, dash.no_update, dash.no_update
