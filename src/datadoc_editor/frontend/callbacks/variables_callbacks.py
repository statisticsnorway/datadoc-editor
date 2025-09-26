"""Variables decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from dash import MATCH
from dash import Dash
from dash import Input
from dash import Output
from dash import ctx

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.variables import (
    accept_variable_metadata_date_input,
)
from datadoc_editor.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc_editor.frontend.callbacks.variables import populate_variables_workspace
from datadoc_editor.frontend.components.identifiers import ACCORDION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import VARIABLES_INFORMATION_ID
from datadoc_editor.frontend.fields.display_base import VARIABLES_METADATA_DATE_INPUT
from datadoc_editor.frontend.fields.display_base import VARIABLES_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import (
    VARIABLES_METADATA_MULTILANGUAGE_INPUT,
)
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

    from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes


logger = logging.getLogger(__name__)


def register_variables_callbacks(app: Dash) -> None:
    """Define and register callbacks for Variables tab."""

    @app.callback(
        Output(ACCORDION_WRAPPER_ID, "children"),
        Input("dataset-opened-counter", "data"),
        Input("search-variables", "value"),
    )
    def callback_populate_variables_workspace(
        dataset_opened_counter: int,
        search_query: str,
    ) -> list:
        """Create variable workspace with accordions for variables."""
        logger.debug("Populating variables workspace. Search query: %s", search_query)
        return populate_variables_workspace(
            state.metadata.variables,
            search_query,
            dataset_opened_counter,
        )

    @app.callback(
        Output(VARIABLES_INFORMATION_ID, "children"),
        Input("dataset-opened-counter", "data"),
    )
    def callback_populate_variables_info_section(
        dataset_opened_counter: int,  # noqa: ARG001 Dash requires arguments for all Inputs
    ) -> str:
        if state.metadata.variables and len(state.metadata.variables) > 0:
            return f"Datasettet inneholder {len(state.metadata.variables)} variabler."

        return "Åpne et datasett for å liste variablene."

    @app.callback(
        Output(
            {
                "type": VARIABLES_METADATA_MULTILANGUAGE_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
                "language": MATCH,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_MULTILANGUAGE_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
                "language": MATCH,
            },
            "errormessage",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_MULTILANGUAGE_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
                "language": MATCH,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_variable_metadata_multilanguage_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> dbc.Alert:
        """Save updated variable metadata values."""
        message = accept_variable_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["variable_short_name"],
            ctx.triggered_id["id"],
            ctx.triggered_id["language"],
        )
        if not message:
            # No error to display.
            return False, ""

        return True, message

    @app.callback(
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "errormessage",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "errormessage",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "value",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_DATE_INPUT,
                "variable_short_name": MATCH,
                "id": VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_variable_metadata_date_input(
        contains_data_from: str,
        contains_data_until: str,
    ) -> dbc.Alert:
        """Special case handling for date fields which have a relationship to one another."""
        return accept_variable_metadata_date_input(
            VariableIdentifiers(ctx.triggered_id["id"]),
            ctx.triggered_id["variable_short_name"],
            contains_data_from,
            contains_data_until,
        )

    @app.callback(
        Output(
            {
                "type": VARIABLES_METADATA_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
            },
            "error",
        ),
        Output(
            {
                "type": VARIABLES_METADATA_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
            },
            "errormessage",
        ),
        Input(
            {
                "type": VARIABLES_METADATA_INPUT,
                "variable_short_name": MATCH,
                "id": MATCH,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_variable_metadata_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> dbc.Alert:
        """Save updated variable metadata values."""
        message = accept_variable_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["variable_short_name"],
            ctx.triggered_id["id"],
        )
        if not message:
            # No error to display.
            return False, ""

        return True, message
