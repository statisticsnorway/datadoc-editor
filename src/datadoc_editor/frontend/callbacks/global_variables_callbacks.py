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
        Input({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        Input("add-global-variables-button", "n_clicks"),
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
        State("global-variables-store", "data"),
        prevent_initial_call=True,
    )
    def callback_accept_global_variable_metadata_input(
        value: str | None,
        n_clicks: int,  # noqa: ARG001
        component_id: dict,
        store_data: dict,
    ) -> tuple:
        """Update store_data with add/change/delete and generate accurate alerts."""
        triggered = ctx.triggered_id
        value_dict = {
            id_["id"]: val for id_, val in zip(component_id, value, strict=False)
        }
        if store_data is None:
            store_data = {}
        alerts: list = []
        delete_fields = [
            field_id
            for field_id, val in value_dict.items()
            if val in ("", "-- Velg --", None)
        ]
        for field_id in delete_fields:
            store_data.pop(field_id, None)
            value_dict.pop(field_id, None)
        info_alert_list: list = []
        if triggered == "add-global-variables-button":
            affected_variables = inherit_global_variable_values(value_dict, store_data)
            store_data.update(affected_variables)
            logger.debug("Error %s", store_data)

            info_alert_list.extend(
                f"{field_data['display_name']}: {field_data['num_vars']} variables vil oppdateres med verdien: {field_data.get('display_value')}"
                for field_data in store_data.values()
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
        return store_data, alerts

    @app.callback(
        Output({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
        Input("reset-button", "n_clicks"),
        State("global-variables-store", "data"),
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
        prevent_initial_call=True,
    )
    def accept_reset_button(
        n_clicks: int,  # noqa: ARG001
        store_data: dict,
        component_id: dict,
    ) -> list:
        """Button."""
        #  if "reset-button.n_clicks" in ctx.triggered_prop_ids:
        if ctx.triggered_id == "reset-button":
            cancel_inherit_global_variable_values(store_data)
            cleared_values = ["", "", None, "", "", ""]
            logger.debug("Resetting %s inputs -> %s", len(component_id), cleared_values)
            return cleared_values
        return [dash.no_update]
