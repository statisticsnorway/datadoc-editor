"""Global."""

import logging

import dash
import ssb_dash_components as ssb
from dash import ALL, MATCH
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.global_variables import (
    cancel_inherit_global_variable_values,
)
from datadoc_editor.frontend.callbacks.global_variables import inherit_global_variable_values
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
        Input("global-variable-store", "data"),
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
    def reset_all(
        n_clicks, 
        ids, 
        ):
        trigger = ctx.triggered_id
        print("Trigger in reset: ", trigger)
        if trigger == "reset-button":
            cleared_values = [""] * len(ids)
            return cleared_values
        return dash.no_update
    
    ##@app.callback(
    #    Output(FORCE_RERENDER_GLOBALS_COUNTER, "data"),
    #    Output("global-variables-store", "data"),
    #    Output("global-output", "children"),
    #    Output({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
    #    Input({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
    #    Input("add-global-variables-button", "n_clicks"),
    #    Input("reset-button", "n_clicks"),
    #    State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
    #    State("global-variables-store", "data"),
    #    State(FORCE_RERENDER_GLOBALS_COUNTER, "data"),
    #    prevent_initial_call=True,
    #)
    #def callback_accept_global_variable_metadata_input(
    #    values: list,
    #    n_clicks: int,  # noqa: ARG001
    #    reset_clicks,
    #    component_id: dict,
    #    store_data: dict,
    #    counter: int,
    #) -> tuple:
    #    """Update store_data with add/change/delete and generate alerts."""
    #    alerts: list = []
    #    info_alert_list: list = []
    #    trigger = ctx.triggered_id
    #    counter += 1
    #    if trigger == "reset-button":
    #        cancel_inherit_global_variable_values(store_data)
    #        store_data.clear()
    #        cleared_values = []
    #        cleared_values = [""] * len(component_id)  # dropdown deselect + input empty string
    #        return counter,store_data, alerts, cleared_values
    #    elif trigger == "add-global-variables-button":
    #        value_dict = {c["id"]: v for c, v in zip(component_id, values, strict=False)}
    #        value_dict = {k: v for k, v in value_dict.items() if v not in ("", "-- Velg --", None)}
    #        affected_variables = inherit_global_variable_values(value_dict, store_data)
    #        store_data.update(affected_variables)
    #        
    #    #logger.debug("Check value dict before %s", value_dict)
    #    #logger.debug("Check store data before %s", store_data)
    #    #delete_fields = [
    #    #    field_id
    #    #    for field_id, val in value_dict.items()
    #    #    if val in ("", "-- Velg --", None)
    #    #]
    #    #for field_id in delete_fields:
    #    #    #store_data.pop(field_id, None)
    #    #    value_dict.pop(field_id, None)
    #    #logger.debug("Check value dict after %s", value_dict)
    #    #if ctx.triggered_id == "add-global-variables-button" and n_clicks > 0:
    #        #affected_variables = inherit_global_variable_values(value_dict, store_data)
    #        #store_data.update(affected_variables)
    #        #logger.debug("Check store data after %s", store_data)
    #        info_alert_list.extend(
    #            f"{field_data['display_name']}: {field_data['num_vars']} variables vil oppdateres med verdien: {field_data.get('display_value')}"
    #            for field_data in store_data.values()
    #        )
    #        alerts.append(
    #            build_ssb_alert(
    #                alert_type=AlertTypes.INFO,
    #                title="Globale verdier",
    #                message="Følgende felter vil kunne oppdateres:",
    #                link=None,
    #                alert_list=info_alert_list,
    #            )
    #        )
    #        return counter, store_data, alerts, values
    #    return counter, dash.no_update, [], [dash.no_update]* len(component_id)
    #
    ##[None]*len(values)
    ## @app.callback(
    #     Output("global-variables-store", "data", allow_duplicate=True),
    #     Output({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
    #     Input("reset-button", "n_clicks"),
    #     State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
    #     State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "value"),
    #     State("global-variables-store", "data"),
    #     prevent_initial_call=True,
    # )
    # def accept_reset_button(
    #     n_clicks: int,  # noqa: ARG001
    #     component_ids,
    #     current_values,
    #     store_data: dict,
    # ) -> list:
    #     """Remove added global variables values."""
    #     if not ctx.triggered or ctx.triggered_id != "reset-button":
    #         raise dash.PreventUpdate
    #     store_data = store_data or {}
    #     
    #     remove_keys = [cid["id"] for cid, val in zip(component_ids, current_values) if val not in ("", "-- Velg --", None)]
    #     for k in remove_keys:
    #         store_data.pop(k, None)
    # 
    #     cancel_inherit_global_variable_values(store_data)
    #     cleared_values = []
    #     for val in values:
    #         if val in ("", "-- Velg --", None):
    #             # already empty: keep it empty
    #             cleared_values.append(val)
    #         else:
    #             # if it was a string (text input or a dropdown value), prefer "" for inputs
    #             # and None is safe for many dropdowns — this heuristic usually works.
    #             cleared_values.append("")
    #
    #     # double-check sizes to catch bugs early
    #     assert len(cleared_values) == len(component_ids), "cleared_values length mismatch"
    #
    #     return store_data, cleared_values

