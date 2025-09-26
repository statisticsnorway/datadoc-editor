"""use_restrictions decorated callback functions should be defined here.

Implementations of the callback functionality should be in other functions (in other files), to enable unit testing.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from dash import ALL
from dash import Dash
from dash import Input
from dash import Output
from dash import State
from dash import ctx

from datadoc_editor.frontend.callbacks.dataset import remove_dataset_multidropdown_input
from datadoc_editor.frontend.callbacks.utils import render_multidropdown_row
from datadoc_editor.frontend.callbacks.utils import update_store_data_with_inputs
from datadoc_editor.frontend.components.identifiers import ADD_USE_RESTRICTION_BUTTON
from datadoc_editor.frontend.components.identifiers import FORCE_RERENDER_COUNTER
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_ID_STORE
from datadoc_editor.frontend.components.identifiers import (
    USE_RESTRICTION_LIST_CONTAINER,
)
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_OPTION_STORE
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_STORE
from datadoc_editor.frontend.fields.display_base import (
    DATASET_METADATA_MULTIDROPDOWN_INPUT,
)

if TYPE_CHECKING:
    from collections.abc import Callable


logger = logging.getLogger(__name__)


def register_use_restriction_callbacks(app: Dash) -> None:
    """Define and register callbacks for use_restrictions."""

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
