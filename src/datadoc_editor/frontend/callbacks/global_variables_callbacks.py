"""Global."""

import logging

import dash
import ssb_dash_components as ssb
from dash import ALL
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx

from datadoc_editor import state
from datadoc_editor.frontend.components.builders import build_global_edit_section
from datadoc_editor.frontend.components.builders import build_global_ssb_accordion
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_ID
from datadoc_editor.frontend.fields.display_global_variables import (
    GLOBAL_METADATA_INPUT,
)
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_VARIABLES

logger = logging.getLogger(__name__)


def register_global_variables_callbacks(app: Dash) -> None:
    """Define and register callbacks for global variables values."""

    @app.callback(
        Output(GLOBAL_VARIABLES_ID, "children"),
        Input("dataset-opened-counter", "data"),
        Input("global-variable-store", "data"), # this should just be the values
    )
    def callback_populate_variables_globals_section(
        dataset_opened_counter: int,  # noqa: ARG001 Dash requires arguments for all Inputs
        store_data,
    ) -> None | ssb.Accordion:
        """Docstring."""
        logger.debug("Populating global variables section.")
        if state.metadata.variables and len(state.metadata.variables) > 0:
            print("Higher level store data: ", store_data)
            return build_global_ssb_accordion(
                header="Globale verdier",
                key={"global": "value"},
                children=build_global_edit_section(GLOBAL_VARIABLES, store_data),
            )
        return None

    @app.callback(
        Output("global-variable-store", "data"),
        Input({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def test_all_callback(
        values, 
        ids):
        trigger = ctx.triggered_id
        print("Trigger: ", trigger)
        print("Value:", values)
        print("IDs:", ids)
        return dict(zip([i["id"] for i in ids], values))
    
    @app.callback(
        Output({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        Input("reset-button", "n_clicks"),
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def reset_all(n_clicks, ids):
        trigger = ctx.triggered_id
        print("Trigger in reset: ", trigger)
        if trigger == "reset-button":
            cleared_values = [""] * len(ids)
            return cleared_values
        return dash.no_update
