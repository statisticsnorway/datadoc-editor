"""Global variables decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions in 'global_variables', to enable unit testing.
"""

from __future__ import annotations

import logging
import ssb_dash_components as ssb
from dash import Dash, Input, Output, State

from datadoc_editor import state
from datadoc_editor.frontend.components.global_variables_builders import build_global_edit_section, build_global_ssb_accordion
from datadoc_editor.frontend.components.identifiers import FORCE_RERENDER_GLOBALS_COUNTER, GLOBAL_VARIABLES_ID, GLOBAL_VARIABLES_VALUES_STORE
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_VARIABLES

logger = logging.getLogger(__name__)

def register_global_variables_callbacks(app: Dash) -> None:
    """Define and register callbacks for global variables values."""
    
    @app.callback(
        Output(GLOBAL_VARIABLES_ID, "children"),
        Input("dataset-opened-counter", "data"),
        Input(GLOBAL_VARIABLES_VALUES_STORE, "data"),
        State(FORCE_RERENDER_GLOBALS_COUNTER, "data"),
    )
    def callback_populate_variables_globals_section(
        dataset_opened_counter: int,  # noqa: ARG001 Dash requires arguments for all Inputs
        store_data,  # noqa: ANN001
        counter: int,
    ) -> None | ssb.Accordion:
        """Populating global variables section."""
        logger.debug("Populating global variables section.")
        if state.metadata.variables and len(state.metadata.variables) > 0:
            return build_global_ssb_accordion(
                header="Globale verdier",
                key={"id":"global_id", "type": "accordion"},
                children=build_global_edit_section(GLOBAL_VARIABLES, store_data, counter),
            )
        return None
