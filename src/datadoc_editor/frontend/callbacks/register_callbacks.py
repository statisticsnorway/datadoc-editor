"""General decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any

from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import html
from dash import no_update

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.dataset import open_dataset_handling
from datadoc_editor.frontend.callbacks.utils import render_tabs
from datadoc_editor.frontend.callbacks.utils import save_metadata_and_generate_alerts
from datadoc_editor.frontend.callbacks.utils import update_store_data_with_inputs
from datadoc_editor.frontend.callbacks.variables import (
    accept_pseudo_variable_metadata_input,
    inherit_global_variable_values,
)
from datadoc_editor.frontend.callbacks.variables import (
    accept_variable_metadata_date_input,
)
from datadoc_editor.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc_editor.frontend.callbacks.variables import mutate_variable_pseudonymization
from datadoc_editor.frontend.callbacks.variables import populate_pseudo_workspace
from datadoc_editor.frontend.callbacks.variables import populate_variables_workspace
from datadoc_editor.frontend.components.builders import build_dataset_edit_section, build_global_edit_section, build_global_ssb_accordion
from datadoc_editor.frontend.components.builders import build_dataset_machine_section
from datadoc_editor.frontend.components.identifiers import ACCORDION_WRAPPER_ID, GLOBAL_VARIABLES_ID
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
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_METADATA_INPUT, GLOBAL_VARIABLES
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)


def register_callbacks(app: Dash) -> None:
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
        State({"type": GLOBAL_METADATA_INPUT, "id": ALL}, "id"),
    )
    def callback_accept_global_variable_metadata_input(
        value,  # noqa: ANN001
        component_id,  # noqa: ANN001
    ) -> None:
        """Save updated variable metadata values."""
        value_dict = {
            id_["id"]: val for id_, val in zip(component_id, value, strict=False)
        }
        logger.debug("Global value: %s", value_dict)
        inherit_global_variable_values(value_dict)
        #fields_to_fill = ["unit_type", "measurement_unit", "multiplication_factor", "variable_role", "data_source", "temporality_type"]
        #for field in fields_to_fill:
        #    logger.debug("This is field %s and value %s", field, value_dict[field])
        #return str(value_dict)