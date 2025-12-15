"""Factory functions for global editable variables components are defined here."""

from __future__ import annotations

import uuid

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc_editor.frontend.components.identifiers import ADD_GLOBAL_VARIABLES_BUTTON
from datadoc_editor.frontend.components.identifiers import GLOBAL_EDIT_SECTION
from datadoc_editor.frontend.components.identifiers import GLOBAL_EDITABLE
from datadoc_editor.frontend.components.identifiers import GLOBAL_INFO_ALERTS_OUTPUT
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_ACCORDION
from datadoc_editor.frontend.components.identifiers import GLOBAL_VARIABLES_INPUT
from datadoc_editor.frontend.constants import GLOBAL_ADD_BUTTON
from datadoc_editor.frontend.constants import GLOBAL_HEADER_INFORMATION
from datadoc_editor.frontend.constants import GLOBAL_HEADER_INFORMATION_LIST
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_base import FieldTypes
from datadoc_editor.frontend.fields.display_base import MetadataDropdownField
from datadoc_editor.frontend.fields.display_base import MetadataInputField
from datadoc_editor.frontend.fields.display_variables import GLOBAL_OPTIONS_GETTERS


def build_global_input_field_section(
    metadata_fields: list[FieldTypes],
    selected_values: dict,
    field_id: str = "",
) -> dbc.Form:
    """Create form with input fields for global variable workspace."""
    inputs = []
    for field in metadata_fields:
        value = selected_values.get(field.identifier)
        component_id = {"type": GLOBAL_VARIABLES_INPUT, "id": field.identifier}
        if isinstance(field, MetadataInputField):
            input_component = ssb.Input(
                label=field.display_name,
                id=component_id,
                debounce=True,
                type=field.type,
                value=value,
                showDescription=True,
                description=field.description,
                readOnly=not field.editable,
                className="global-input-component",
                required=field.obligatory and field.editable,
            )
        elif isinstance(field, MetadataDropdownField):
            options_getter = GLOBAL_OPTIONS_GETTERS.get(field.identifier)
            input_component = ssb.Dropdown(
                header=field.display_name,
                id=component_id,
                items=options_getter() if callable(options_getter) else [],
                placeholder=DROPDOWN_DESELECT_OPTION,
                className="global-dropdown-component",
                value=value,
                showDescription=True,
                description=field.description,
                required=field.obligatory and field.editable,
                searchable=field.searchable,
            )

        inputs.append(input_component)
    return dbc.Form(
        inputs,
        id=f"{GLOBAL_VARIABLES_INPUT}-{field_id}",
        className="global-edit-section-form",
        key=str(uuid.uuid4()),
    )


def build_global_edit_section(
    metadata_inputs: list[FieldTypes],
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
                    ssb.Button(
                        GLOBAL_ADD_BUTTON,
                        id=ADD_GLOBAL_VARIABLES_BUTTON,
                        negative=True,
                        className="global-button",
                        icon=html.I(className="bi-plus-circle"),
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
