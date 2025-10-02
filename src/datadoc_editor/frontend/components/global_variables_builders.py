"""Factory functions for global editable variables components are defined here."""

from __future__ import annotations

import ssb_dash_components as ssb
from dash import html

from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_ACCORDION


def build_global_ssb_accordion(
    header: str,
    key: dict,
    children: html.Section,
) -> ssb.Accordion:
    """Build Accordion for global editable section in variable workspace."""
    return ssb.Accordion(
        header=header,
        id=key,
        children=[
            html.Section(
                id=GLOBAL_VARIABLES_ACCORDION,
                children=children,
            ),
        ],
        className="global-variable-accordion",
    )
