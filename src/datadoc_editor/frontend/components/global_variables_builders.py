"""Factory functions for global editable variables components are defined here."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html
from dash import dcc

from datadoc_editor.frontend.components.identifiers import ADD_GLOBAL_VARIABLES_BUTTON, GLOBAL_ADDED_VARIABLES_STORE, GLOBAL_EDIT_SECTION, GLOBAL_EDITABLE, GLOBAL_INFO_ALERTS_OUTPUT, GLOBAL_VARIABLES_ACCORDION, RESET_GLOBAL_VARIABLES_BUTTON
from datadoc_editor.frontend.fields.display_base import GlobalFieldTypes
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_HEADER_INFORMATION, GLOBAL_VARIABLES_INPUT

def build_global_input_field_section(
    metadata_fields: list[GlobalFieldTypes],
    selected_values: dict,
    counter: int,
    field_id: str = "",
) -> dbc.Form:
    """Create form with input fields for global variable workspace."""
    return dbc.Form(
        [
            i.render(
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
        key=f"{GLOBAL_VARIABLES_INPUT}-{counter}",
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
                        GLOBAL_HEADER_INFORMATION, className="global-paragraph"
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
                metadata_inputs, selected_values, field_id=GLOBAL_EDITABLE,
            ),
            dcc.Store(id=GLOBAL_ADDED_VARIABLES_STORE, data={}),
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
