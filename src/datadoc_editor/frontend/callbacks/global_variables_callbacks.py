"""Global variables decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions in 'global_variables', to enable unit testing.
"""

from __future__ import annotations

import logging
import dash
import ssb_dash_components as ssb
from dash import ALL, Dash, Input, Output, State, ctx

from datadoc_editor import state
from datadoc_editor.frontend.components.global_variables_builders import build_global_edit_section, build_global_ssb_accordion
from datadoc_editor.frontend.components.identifiers import FORCE_RERENDER_GLOBALS_COUNTER, GLOBAL_VARIABLES_ID, GLOBAL_VARIABLES_VALUES_STORE, RESET_GLOBAL_VARIABLES_BUTTON
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_VARIABLES, GLOBAL_VARIABLES_INPUT

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
        logger.debug("Populating global variables section.")
        if state.metadata.variables and len(state.metadata.variables) > 0:
            return build_global_ssb_accordion(
                header="Globale verdier",
                key={"id":"global_id", "type": "accordion"},
                children=build_global_edit_section(GLOBAL_VARIABLES, store_data),
            )
        return None

    @app.callback(
        Output(GLOBAL_VARIABLES_VALUES_STORE, "data"),
        Input({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "value"),
        State({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def accept_global_values(values, ids):  # noqa: ANN202,ANN001
        logger.debug("Value: %s", values)
        logger.debug("IDs: %s", ids)
        return dict(zip([i["id"] for i in ids], values, strict=False))

    @app.callback(
        Output({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "value"),
        Input(RESET_GLOBAL_VARIABLES_BUTTON, "n_clicks"),
        State({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def reset_global_variables(
        n_clicks: int,  # noqa: ARG001
        ids,  # noqa: ANN001
    ) -> list | None | dash.NoUpdate:
        trigger = ctx.triggered_id
        if trigger == "reset-global-variables-button":
            return [""] * len(ids)
        return dash.no_update