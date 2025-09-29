"""Global."""


import logging
from typing import TYPE_CHECKING
from dash import ALL, Dash, Input, Output, State

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.variables import inherit_global_variable_values
from datadoc_editor.frontend.components.builders import build_global_ssb_accordion
from datadoc_editor.frontend.components.field_builders import build_global_edit_section
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_ID
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_METADATA_INPUT, GLOBAL_VARIABLES
if TYPE_CHECKING:
    import dash_bootstrap_components as dbc


logger = logging.getLogger(__name__)



def register_global_variables_callbacks(app: Dash) -> None:
    """Define and register callbacks for global variables values."""
    @app.callback(
        Output(GLOBAL_VARIABLES_ID, "children"),
        Input("dataset-opened-counter", "data"),
    )
    def callback_populate_variables_globals_section(
        dataset_opened_counter: int,  # noqa: ARG001 Dash requires arguments for all Inputs
    ) -> None:
        logger.debug("Populating global variables section.")
        if state.metadata.variables and len(state.metadata.variables) > 0:
            return build_global_ssb_accordion(
                header="Rediger alle",
                key={"global": "value"},
                children=build_global_edit_section(GLOBAL_VARIABLES),
            )

    @app.callback(
        Output("global-output", "children"),
        Input({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        Input("add-global-variables-values", "n_clicks"),
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"), 
    )
    def callback_accept_global_variable_metadata_input(
        value,  # noqa: ANN001
        n_clicks: int,
        component_id,  # noqa: ANN001
    ) -> None:
        """Save updated variable metadata values."""
        value_dict = {
            id_["id"]: val for id_, val in zip(component_id, value, strict=False)
        }
        logger.debug("Global value: %s", value_dict)
        if n_clicks and n_clicks > 0:
            inherit_global_variable_values(value_dict)
        #fields_to_fill = ["unit_type", "measurement_unit", "multiplication_factor", "variable_role", "data_source", "temporality_type"]
        #for field in fields_to_fill:
        #    logger.debug("This is field %s and value %s", field, value_dict[field])
        #return str(value_dict)