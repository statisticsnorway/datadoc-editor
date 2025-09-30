"""Global."""

import logging

import ssb_dash_components as ssb
from dash import ALL
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.variables import (
    cancel_inherit_global_variable_values,
)
from datadoc_editor.frontend.callbacks.variables import inherit_global_variable_values
from datadoc_editor.frontend.components.builders import AlertTypes
from datadoc_editor.frontend.components.builders import build_global_edit_section
from datadoc_editor.frontend.components.builders import build_global_ssb_accordion
from datadoc_editor.frontend.components.builders import build_ssb_alert
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
    )
    def callback_populate_variables_globals_section(
        dataset_opened_counter: int,  # noqa: ARG001 Dash requires arguments for all Inputs
    ) -> None | ssb.Accordion:
        """Docstring."""
        logger.debug("Populating global variables section.")
        if state.metadata.variables and len(state.metadata.variables) > 0:
            return build_global_ssb_accordion(
                header="Globale verdier",
                key={"global": "value"},
                children=build_global_edit_section(GLOBAL_VARIABLES),
            )
        return None

    @app.callback(
        Output("global-variables-store", "data"),
        Output("global-output", "children"),
        Output({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        Input({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        Input("add-global-variables-button", "n_clicks"),
        Input("reset-button", "n_clicks"),
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
        State("global-variables-store", "data"),
        prevent_initial_call=True,
    )
    def callback_accept_global_variable_metadata_input(
        value,  # ignore: ANN001
        n_clicks: int,
        reset_clicks: int, # ignore: ARG001
        component_id,  # ignore: ANN001
        store_data,  # ignore: ANN001
    ): # ignore: ANN202
        """Update store_data with add/change/delete and generate accurate alerts."""
        value_dict = {
            id_["id"]: val for id_, val in zip(component_id, value, strict=False)
        }
        if store_data is None:
            store_data = {}
        alerts: list = []
        delete_fields = [
            field_id
            for field_id, val in value_dict.items()
            if val in ("", "-- Velg --")
        ]
        for field_id in delete_fields:
            store_data.pop(field_id, None)
            value_dict.pop(field_id, None)
        info_alert_list = []
        triggered = ctx.triggered_id
        if n_clicks and n_clicks > 0:
            affected_variables = inherit_global_variable_values(value_dict, store_data)
            store_data.update(affected_variables)
            logger.debug("Error %s", store_data)

            # values()
            for field_name, field_data in store_data.items():
                info_alert_list.append(
                    f"{field_data['display_name']}: {field_data['num_vars']} variables vil oppdateres med verdien: {field_data.get('display_value')}"
                )
            alerts.append(
                build_ssb_alert(
                    alert_type=AlertTypes.INFO,
                    title="Globale verdier",
                    message="Følgende felter vil kunne oppdateres:",
                    link=None,
                    alert_list=info_alert_list,
                )
            )
        if triggered == "reset-button":
            logger.debug("Store data %s", store_data)
            cancel_inherit_global_variable_values(store_data)
            alerts = []
            value = [""] * len(value)
            logger.debug("Value %s", value)
            logger.debug("Id %s", component_id)
            return store_data, alerts, value
        return store_data, alerts, value
