"""Dataset decorated callback functions should be defined here.

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
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_metadata_date_input
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_multidropdown_input
from datadoc_editor.frontend.components.builders import build_dataset_edit_section
from datadoc_editor.frontend.components.builders import build_dataset_machine_section
from datadoc_editor.frontend.components.identifiers import SECTION_WRAPPER_ID
from datadoc_editor.frontend.fields.display_base import DATASET_METADATA_DATE_INPUT
from datadoc_editor.frontend.fields.display_base import DATASET_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import (
    DATASET_METADATA_MULTIDROPDOWN_INPUT,
)
from datadoc_editor.frontend.fields.display_base import (
    DATASET_METADATA_MULTILANGUAGE_INPUT,
)
from datadoc_editor.frontend.fields.display_dataset import (
    EDITABLE_DATASET_METADATA_LEFT,
)
from datadoc_editor.frontend.fields.display_dataset import (
    EDITABLE_DATASET_METADATA_RIGHT,
)
from datadoc_editor.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

    from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes


logger = logging.getLogger(__name__)


def register_dataset_callbacks(app: Dash) -> None:
    """Define and register callbacks for Dataset tab."""

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
