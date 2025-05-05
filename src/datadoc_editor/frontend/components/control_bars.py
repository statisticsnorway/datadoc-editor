"""Components and layout which are not inside a tab."""

from __future__ import annotations

import ssb_dash_components as ssb
from dash import html

from datadoc_editor.frontend.callbacks.utils import get_dataset_path
from datadoc_editor.utils import get_app_version

header = ssb.Header(
    [
        ssb.Title("Datadoc Editor", size=1, id="main-title", className="main-title"),
        ssb.Link(
            "Dokumentasjon",
            href="https://manual.dapla.ssb.no/statistikkere/datadoc.html",
            isExternal=True,
        ),
    ],
    className="datadoc-header",
)


def build_footer_control_bar() -> html.Aside:
    """Build footer control bar which resides below all the content."""
    return html.Aside(
        children=[
            html.P(
                f"v{get_app_version()}",
                className="small",
            ),
        ],
        className="language-footer",
    )


def build_controls_bar() -> html.Section:
    """Build the Controls Bar.

    This contains:
    - A text input to specify the path to a dataset
    - A button to open a dataset
    - A button to save metadata to disk
    """
    return html.Section(
        [
            ssb.Input(
                label="Filsti",
                value=get_dataset_path(),
                className="file-path-input",
                id="dataset-path-input",
            ),
            html.Section(
                [
                    ssb.Button(
                        children=["Åpne fil"],
                        id="open-button",
                        className="file-open-button",
                    ),
                    ssb.Button(
                        children=["Lagre metadata"],
                        id="save-button",
                        className="file-save-button",
                    ),
                ],
                className="button-section",
            ),
        ],
        className="control-bar-section",
    )
