"""All decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any

from dash import ALL
from dash import MATCH
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx
from dash import html
from dash import no_update

from datadoc_editor import state
from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_metadata_date_input
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_multidropdown_input
from datadoc_editor.frontend.callbacks.dataset import open_dataset_handling
from datadoc_editor.frontend.callbacks.dataset import remove_dataset_multidropdown_input
from datadoc_editor.frontend.callbacks.utils import render_multidropdown_row
from datadoc_editor.frontend.callbacks.utils import render_tabs
from datadoc_editor.frontend.callbacks.utils import save_metadata_and_generate_alerts
from datadoc_editor.frontend.callbacks.utils import update_store_data_with_inputs
from datadoc_editor.frontend.callbacks.variables import (
    accept_pseudo_variable_metadata_input,
)
from datadoc_editor.frontend.callbacks.variables import (
    accept_variable_metadata_date_input,
)
from datadoc_editor.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc_editor.frontend.callbacks.variables import mutate_variable_pseudonymization
from datadoc_editor.frontend.callbacks.variables import populate_pseudo_workspace
from datadoc_editor.frontend.callbacks.variables import populate_variables_workspace
from datadoc_editor.frontend.components.builders import build_dataset_edit_section
from datadoc_editor.frontend.components.builders import build_dataset_machine_section
from datadoc_editor.frontend.components.identifiers import ACCORDION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import ADD_USE_RESTRICTION_BUTTON
from datadoc_editor.frontend.components.identifiers import FORCE_RERENDER_COUNTER
from datadoc_editor.frontend.components.identifiers import SECTION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_ID_STORE
from datadoc_editor.frontend.components.identifiers import (
    USE_RESTRICTION_LIST_CONTAINER,
)
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_OPTION_STORE
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_STORE
from datadoc_editor.frontend.components.identifiers import VARIABLES_INFORMATION_ID
from datadoc_editor.frontend.fields.display_base import DATASET_METADATA_DATE_INPUT
from datadoc_editor.frontend.fields.display_base import DATASET_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import (
    DATASET_METADATA_MULTIDROPDOWN_INPUT,
)
from datadoc_editor.frontend.fields.display_base import (
    DATASET_METADATA_MULTILANGUAGE_INPUT,
)
from datadoc_editor.frontend.fields.display_base import PSEUDO_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import VARIABLES_METADATA_DATE_INPUT
from datadoc_editor.frontend.fields.display_base import VARIABLES_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import (
    VARIABLES_METADATA_MULTILANGUAGE_INPUT,
)
from datadoc_editor.frontend.fields.display_dataset import (
    EDITABLE_DATASET_METADATA_LEFT,
)
from datadoc_editor.frontend.fields.display_dataset import (
    EDITABLE_DATASET_METADATA_RIGHT,
)
from datadoc_editor.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    from collections.abc import Callable

    import dash_bootstrap_components as dbc

    from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)


def register_callbacks(app: Dash) -> None:  # noqa: PLR0915
    """Define and register callbacks."""

    @app.callback(
        Output("alerts-section", "children", allow_duplicate=True),
        Input("save-button", "n_clicks"),
        State("alerts-section", "children"),
        prevent_initial_call=True,
    )
    def callback_save_metadata_file(
        n_clicks: int,
        alerts: list,  # argument required by Dash  # noqa: ARG001
    ) -> Any | list:  # noqa: ANN401
        """Save the metadata document to disk and check obligatory metadata.

        Returns:
            List of alerts. Obligatory metadata alert warning if there is obligatory metadata missing.
            And success alert if metadata is saved correctly.
            If none return no_update.
        """
        if n_clicks and n_clicks > 0:
            return save_metadata_and_generate_alerts(state.metadata)

        return no_update

    @app.callback(
        Output(
            {"type": DATASET_METADATA_INPUT, "id": MATCH},
            "error",
        ),
        Output(
            {"type": DATASET_METADATA_INPUT, "id": MATCH},
            "errorMessage",
        ),
        Input(
            {"type": DATASET_METADATA_INPUT, "id": MATCH},
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> tuple[bool, str]:
        """Save updated dataset metadata values.

        Will display an alert if validation fails.
        """
        return accept_dataset_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["id"],
        )

    @app.callback(
        Output(
            {
                "type": DATASET_METADATA_MULTILANGUAGE_INPUT,
                "id": MATCH,
                "language": MATCH,
            },
            "error",
        ),
        Output(
            {
                "type": DATASET_METADATA_MULTILANGUAGE_INPUT,
                "id": MATCH,
                "language": MATCH,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": DATASET_METADATA_MULTILANGUAGE_INPUT,
                "id": MATCH,
                "language": MATCH,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_multilanguage_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> tuple[bool, str]:
        """Save updated dataset metadata values.

        Will display an alert if validation fails.
        """
        # Get the ID of the input that changed. This MUST match the attribute name defined in DataDocDataSet
        return accept_dataset_metadata_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["id"],
            ctx.triggered_id["language"],
        )

    @app.callback(
        Output(
            {
                "type": DATASET_METADATA_MULTIDROPDOWN_INPUT,
                "id": MATCH,
                "field": MATCH,
                "index": MATCH,
            },
            "error",
        ),
        Output(
            {
                "type": DATASET_METADATA_MULTIDROPDOWN_INPUT,
                "id": MATCH,
                "field": MATCH,
                "index": MATCH,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": DATASET_METADATA_MULTIDROPDOWN_INPUT,
                "id": MATCH,
                "field": MATCH,
                "index": MATCH,
            },
            "value",
        ),
    )
    def callback_accept_dataset_metadata_multidropdown_input(
        value: MetadataInputTypes,  # noqa: ARG001 argument required by Dash
    ) -> tuple[bool, str]:
        """Save updated dataset metadata values.

        Will display an alert if validation fails.
        """
        if ctx.triggered_id is None:
            return False, ""
        return accept_dataset_multidropdown_input(
            ctx.triggered[0]["value"],
            ctx.triggered_id["id"],
            ctx.triggered_id["field"],
            ctx.triggered_id["index"],
        )

    @app.callback(
        Output("alerts-section", "children", allow_duplicate=True),
        Output("dataset-opened-counter", "data"),  # Used to force reload of metadata
        Input("open-button", "n_clicks"),
        State("dataset-path-input", "value"),
        State("dataset-opened-counter", "data"),
        prevent_initial_call=True,
    )
    def callback_open_dataset(
        n_clicks: int,
        dataset_path: str,
        dataset_opened_counter: int,
    ) -> tuple[dbc.Alert, int]:
        """Open a dataset.

        Shows an alert on success or failure.

        To trigger reload of data in the UI, we update the
        language dropdown. This is a hack and could be replaced
        by a more formal mechanism.
        """
        return open_dataset_handling(n_clicks, dataset_path, dataset_opened_counter)

    @app.callback(
        Output("display-tab", "children"),
        Input("tabs", "value"),
    )
    def callback_render_tabs(tab: str) -> html.Article | None:
        """Return correct tab content."""
        return render_tabs(tab)

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
        [Output(USE_RESTRICTION_STORE, "data"), Output(FORCE_RERENDER_COUNTER, "data")],
        [
            Input(ADD_USE_RESTRICTION_BUTTON, "n_clicks"),
            Input(
                {
                    "type": DATASET_METADATA_MULTIDROPDOWN_INPUT,
                    "id": ALL,
                    "index": ALL,
                    "field": "type",
                },
                "value",
            ),
            Input(
                {
                    "type": DATASET_METADATA_MULTIDROPDOWN_INPUT,
                    "id": ALL,
                    "index": ALL,
                    "field": "date",
                },
                "value",
            ),
            Input(
                {
                    "type": DATASET_METADATA_MULTIDROPDOWN_INPUT,
                    "id": ALL,
                    "index": ALL,
                    "field": "delete",
                },
                "n_clicks",
            ),
        ],
        [State(USE_RESTRICTION_STORE, "data"), State(FORCE_RERENDER_COUNTER, "data")],
        prevent_initial_call=True,
    )
    def handle_add_and_delete(  # noqa: PLR0913
        add_clicks: int,  # noqa: ARG001
        type_values: list[str],
        date_values: list[str],
        delete_clicks: list[int],  # noqa: ARG001
        store_data: list | None,
        counter: int,
    ) -> tuple[list, int]:
        triggered = ctx.triggered_id
        counter += 1
        store_data = update_store_data_with_inputs(
            store_data or [], type_values, date_values
        )

        if triggered == ADD_USE_RESTRICTION_BUTTON:
            store_data.append(
                {"use_restriction_type": None, "use_restriction_date": None}
            )

        elif isinstance(triggered, dict) and triggered.get("field") == "delete":
            idx = triggered.get("index")
            if isinstance(idx, int) and 0 <= idx < len(store_data):
                remove_dataset_multidropdown_input(
                    DATASET_METADATA_MULTIDROPDOWN_INPUT, idx
                )
                store_data.pop(idx)

        return store_data, counter

    @app.callback(
        Output(USE_RESTRICTION_LIST_CONTAINER, "children"),
        Input(USE_RESTRICTION_STORE, "data"),
        Input(USE_RESTRICTION_OPTION_STORE, "data"),
        Input(USE_RESTRICTION_ID_STORE, "data"),
        Input(FORCE_RERENDER_COUNTER, "data"),
    )
    def render_use_restriction_list(
        current_list: list,
        options: Callable[[], list[dict[str, str]]],
        idx: dict[str, str | int],
        rerender_counter: int,
    ) -> list:
        if not current_list:
            return []

        items = []
        for i, item in enumerate(current_list):
            row_id = {**idx, "index": i}
            items.append(
                render_multidropdown_row(
                    item, row_id, options, key=f"{rerender_counter}-{i}"
                )
            )
        return items

    @app.callback(
        Output(SECTION_WRAPPER_ID, "children"),
        Input("dataset-opened-counter", "data"),
    )
    def callback_populate_dataset_workspace(
        dataset_opened_counter: int,  # Dash requires arguments for all Inputs
    ) -> list:
        """Create dataset workspace with sections."""
        logger.debug("Populating dataset workspace")
        return [
            build_dataset_edit_section(
                [
                    EDITABLE_DATASET_METADATA_LEFT,
                    EDITABLE_DATASET_METADATA_RIGHT,
                ],
                state.metadata.dataset,
                {
                    "type": "dataset-edit-section",
                    "id": f"obligatory-{dataset_opened_counter}",
                },
            ),
            build_dataset_machine_section(
                "Maskingenerert",
                NON_EDITABLE_DATASET_METADATA,
                state.metadata.dataset,
                {
                    "type": "dataset-machine-section",
                    "id": f"machine-{dataset_opened_counter}",
                },
            ),
        ]

    @app.callback(
        Output(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "error",
        ),
        Output(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "errorMessage",
        ),
        Input(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "value",
        ),
        State(
            {"type": PSEUDO_METADATA_INPUT, "variable_short_name": MATCH, "id": MATCH},
            "id",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_pseudo_variable_metadata_input(value, component_id):  # noqa: ANN202, ANN001
        if value is None or component_id is None:
            # Nothing to do if deselected or missing
            return False, ""
        variable_short_name = component_id["variable_short_name"]
        input_id = component_id["id"]
        logger.debug(
            "Callback triggered with value=%s, component_id=%s",
            value,
            component_id,
        )
        # Safely get variable from state
        variable = state.metadata.variables_lookup.get(variable_short_name)
        if not variable:
            logger.info("Variable not found: %s", variable_short_name)
            return False, "Variable not found."

        message = accept_pseudo_variable_metadata_input(
            value, variable_short_name, input_id
        )

        if not message:
            return False, ""

        return True, message

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
            "errorMessage",
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
            "errorMessage",
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
            "errorMessage",
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
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "error",
        ),
        Output(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "errorMessage",
        ),
        Output(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "error",
        ),
        Output(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "errorMessage",
        ),
        Input(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_FROM.value,
            },
            "value",
        ),
        Input(
            {
                "type": DATASET_METADATA_DATE_INPUT,
                "id": DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
            },
            "value",
        ),
        prevent_initial_call=True,
    )
    def callback_accept_dataset_metadata_date_input(
        contains_data_from: str,
        contains_data_until: str,
    ) -> dbc.Alert:
        """Special case handling for date fields which have a relationship to one another."""
        return accept_dataset_metadata_date_input(
            DatasetIdentifiers(ctx.triggered_id["id"]),
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
            "errorMessage",
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

    @app.callback(
        Output({"type": "pseudo-field-container", "variable": MATCH}, "children"),
        Input({"type": "pseudonymization-dropdown", "variable": MATCH}, "value"),
        Input("save-button", "n_clicks"),
        State({"type": "pseudonymization-dropdown", "variable": MATCH}, "id"),
    )
    def callback_populate_pseudo_workspace(
        value,  # noqa: ANN001
        n_clicks: int,
        dropdown_id,  # noqa: ANN001
    ) -> dbc.Form:
        """Dynamically create pseudonymization workspace.

        - The dropdown value updates the displayed pseudonymization fields immediately.
        - The Save button applies permanent changes (update or deletion) to the variable.
        """
        # Map dropdown value to enum if possible
        selected_algorithm = (
            PseudonymizationAlgorithmsEnum[value]
            if value and value in PseudonymizationAlgorithmsEnum.__members__
            else value
        )

        logger.debug("Selected algorithm: %s", selected_algorithm)
        variable = state.metadata.variables_lookup.get(dropdown_id["variable"])

        if variable is None:
            logger.info("Variable not found in lookup!")
            return []

        # Persist update and deletion only on save
        if n_clicks and n_clicks > 0:
            mutate_variable_pseudonymization(variable, selected_algorithm)

        logger.debug(
            "Variable %s has pseudo info: %s",
            variable.short_name,
            variable.pseudonymization,
        )
        return populate_pseudo_workspace(variable, selected_algorithm)
