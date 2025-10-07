"""Factory functions for global editable variables components are defined here."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc_editor.frontend.components.identifiers import ADD_GLOBAL_VARIABLES_BUTTON
from datadoc_editor.frontend.components.identifiers import GLOBAL_EDIT_SECTION
from datadoc_editor.frontend.components.identifiers import GLOBAL_EDITABLE
from datadoc_editor.frontend.components.identifiers import GLOBAL_INFO_ALERTS_OUTPUT
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_ACCORDION
from datadoc_editor.frontend.components.identifiers import RESET_GLOBAL_VARIABLES_BUTTON
from datadoc_editor.frontend.fields.display_global_variables import (
    GLOBAL_HEADER_INFORMATION,
)
from datadoc_editor.frontend.fields.display_global_variables import (
    GLOBAL_HEADER_INFORMATION_LIST,
)
from datadoc_editor.frontend.fields.display_global_variables import (
    GLOBAL_VARIABLES_INPUT,
)

if TYPE_CHECKING:
    from datadoc_editor.frontend.fields.display_base import GlobalFieldTypes


def build_global_input_field_section(
    metadata_fields: list[GlobalFieldTypes],
    selected_values: dict,
    field_id: str = "",
) -> dbc.Form:
    """Create form with input fields for global variable workspace."""
    return dbc.Form(
        [
            i.render_globals(
                component_id={
                    "type": GLOBAL_VARIABLES_INPUT,
                    "id": i.identifier,
                },
                value=selected_values.get(i.identifier),
            )
            for i in metadata_fields
        ],
        id=f"{GLOBAL_VARIABLES_INPUT}-{field_id}",
        className="global-edit-section-form",
        key=str(uuid.uuid4()),
    )


def build_global_edit_section(
    metadata_inputs: list[GlobalFieldTypes],
    selected_values: dict,
) -> html.Section:
    """Create input section for global variables."""
    return html.Section(
        id=GLOBAL_EDIT_SECTION,
        children=[
            html.Div(
                [
                    ssb.Paragraph(
                        GLOBAL_HEADER_INFORMATION,
                        className="global-information-paragraph",
                    ),
                    html.Ul(
                        [html.Li(item) for item in GLOBAL_HEADER_INFORMATION_LIST],
                        className="global-information-list",
                    ),
                    html.Div(
                        [
                            ssb.Button(
                                "Legg til",
                                id=ADD_GLOBAL_VARIABLES_BUTTON,
                                className="global-button",
                            ),
                            ssb.Button(
                                "Nullstill",
                                id=RESET_GLOBAL_VARIABLES_BUTTON,
                                className="global-button",
                            ),
                        ],
                        className="global-header-buttons",
                    ),
                ],
                className="global-section-header",
            ),
            html.Div(id=GLOBAL_INFO_ALERTS_OUTPUT),
            build_global_input_field_section(
                metadata_inputs,
                selected_values,
                field_id=GLOBAL_EDITABLE,
            ),
        ],
        className="global-edit-section",
    )


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
