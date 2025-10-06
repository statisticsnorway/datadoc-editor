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
    inherit_global_variable_values,
)
from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_edit_section,
)
from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_ssb_accordion,
)
from datadoc_editor.frontend.components.identifiers import GLOBAL_ADDED_VARIABLES_STORE
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
        logger.debug("Populating global variables section.")
        if state.metadata.variables and len(state.metadata.variables) > 0:
            return build_global_ssb_accordion(
                header=GLOBAL_HEADER,
                key={"id": "global_id", "type": "accordion"},
                children=build_global_edit_section(GLOBAL_VARIABLES, store_data),
            )
        return None

    @app.callback(
        Output(GLOBAL_VARIABLES_VALUES_STORE, "data"),
        Output(GLOBAL_ADDED_VARIABLES_STORE, "data"),
        Input({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "value"),
        State({"type": GLOBAL_VARIABLES_INPUT, "id": ALL}, "id"),
        State(GLOBAL_ADDED_VARIABLES_STORE, "data"),
        prevent_initial_call=True,
    )
    def accept_global_values(values, ids, added_variables_store):  # noqa: ANN202,ANN001
        logger.debug("Value: %s", values)
        logger.debug("IDs: %s", ids)
        selected_values = dict(zip([i["id"] for i in ids], values, strict=False))
        logger.debug("Selected values %s", selected_values)
        if added_variables_store is None:
            added_variables_store = {}
        affected_variables = inherit_global_variable_values(
            selected_values, added_variables_store
        )
        added_variables_store.update(affected_variables)
        return selected_values, added_variables_store

    @app.callback(
        Input(GLOBAL_VARIABLES_VALUES_STORE, "data"),
        Input(GLOBAL_ADDED_VARIABLES_STORE, "data"),
        prevent_initial_call=True,
    )
    def check_global_values(store_data, added_store_data):  # noqa: ANN202,ANN001
        logger.debug("Listen to store %s", store_data)
        logger.debug("Listen to added store data %s", added_store_data)

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
