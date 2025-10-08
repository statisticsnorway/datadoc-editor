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

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)


def register_callbacks(app: Dash) -> None:
    """Define and register callbacks."""

    @app.callback(
        Output("alerts-section", "children", allow_duplicate=True),
        Output("metadata-save-counter", "data"),
        Input("save-button", "n_clicks"),
        State("alerts-section", "children"),
        State("metadata-save-counter", "data"),
        prevent_initial_call=True,
    )
    def callback_save_metadata_file(
        n_clicks: int,
        alerts: list,  # argument required by Dash  # noqa: ARG001
        metadata_save_counter: int,
    ) -> Any | list:  # noqa: ANN401
        """Save the metadata document to disk and check obligatory metadata.

        Returns:
            List of alerts. Obligatory metadata alert warning if there is obligatory metadata missing.
            And success alert if metadata is saved correctly.
            If none return no_update.
        """
        if n_clicks and n_clicks > 0:
            alerts_list = save_metadata_and_generate_alerts(state.metadata)
            # Increment counter to notify other callbacks
            return alerts_list, metadata_save_counter + 1

        return no_update, no_update

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
