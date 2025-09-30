"""Global."""


import logging
from typing import TYPE_CHECKING
from dash import ALL, Dash, Input, Output, State, ctx

from datadoc_editor import state
from datadoc_editor.constants import DELETE_SELECTED
from datadoc_editor.frontend.callbacks.variables import cancel_global_variable_changes, get_display_name_and_title, inherit_global_variable_values, prepare_global_variable_values
from datadoc_editor.frontend.components.builders import AlertTypes, build_global_ssb_accordion, build_ssb_alert
from datadoc_editor.frontend.components.builders import build_global_edit_section
from datadoc_editor.frontend.components.identifiers import ADD_GLOBAL_VARIABLES_BUTTON, GLOBAL_VARIABLES_ID
from datadoc_editor.frontend.fields.display_global_variables import DISPLAY_GLOBALS, GLOBAL_METADATA_INPUT, GLOBAL_VARIABLES
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
                header="Globale verdier",
                key={"global": "value"},
                children=build_global_edit_section(GLOBAL_VARIABLES),
            )

    @app.callback(
        Output("global-variables-store", "data"),
        Output("global-output", "children"),
        Input({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        Input("add-global-variables-button", "n_clicks"),
        Input("reset-button", "n_clicks"),
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
        State("global-variables-store", "data"),
        prevent_initial_call=True,
    )
    def callback_accept_global_variable_metadata_input(
        value, 
        n_clicks,
        reset_clicks,
        component_id, 
        store_data,
        ):
        """Update store_data with add/change/delete and generate accurate alerts."""
        value_dict = {id_["id"]: val for id_, val in zip(component_id, value, strict=False)}
        if store_data is None:
            store_data = {}
        global_dict = get_display_name_and_title(value_dict, GLOBAL_VARIABLES)
        alerts: list = []
        display_value_map = {display_name: title for display_name, title in global_dict}
        delete_fields = [field_id for field_id, val in value_dict.items() if val in ("", "-- Velg --")]
        for field_id in delete_fields:
            store_data.pop(field_id, None)
            value_dict.pop(field_id, None)  
        info_alert_list = []
        
        if n_clicks and n_clicks > 0:
            affected_variables = inherit_global_variable_values(value_dict, store_data)
            store_data.update(affected_variables)
            logger.debug("Error %s", store_data)

            for field_name, field_data in store_data.items():
                info_alert_list.append(
                    f"{field_data['display_name']}: {field_data['num_vars']} variables vil oppdateres med verdien: {field_data.get('display_value')}"
                )
            alerts.append(build_ssb_alert(
                alert_type=AlertTypes.INFO,
                title="Globale verdier",
                message="Følgende felter vil kunne oppdateres:",
                link=None,
                alert_list=info_alert_list
            ))
        if reset_clicks and reset_clicks > 0:
            logger.debug("Store data %s", store_data)
        return store_data, alerts
