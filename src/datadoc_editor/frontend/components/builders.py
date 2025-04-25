"""Factory functions for different components are defined here."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc_editor.frontend.fields.display_base import DATASET_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import PSEUDO_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import VARIABLES_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import FieldTypes

if TYPE_CHECKING:
    from dapla_metadata.datasets import model


class AlertTypes(Enum):
    """Types of alerts."""

    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass
class AlertType:
    """Attributes of a concrete alert type."""

    color: str

    @staticmethod
    def get_type(alert_type: AlertTypes) -> AlertType:
        """Get a concrete alert type based on the given enum values."""
        return ALERT_TYPES[alert_type]


ALERT_TYPES = {
    AlertTypes.ERROR: AlertType(
        color="danger",
    ),
    AlertTypes.WARNING: AlertType(
        color="warning",
    ),
    AlertTypes.SUCCESS: AlertType(
        color="success",
    ),
}


def build_ssb_alert(
    alert_type: AlertTypes,
    title: str,
    message: str | None = None,
    link: dict | None = None,
    alert_list: list | None = None,
) -> dbc.Alert:
    """Make a Dash Alert according to SSBs Design System."""
    alert = AlertType.get_type(alert_type)
    if alert_list is None:
        alert_list = []
    return dbc.Alert(
        is_open=True,
        dismissable=True,
        fade=True,
        color=alert.color,
        duration=5000 if alert_type == AlertTypes.SUCCESS else None,
        children=[
            html.H5(
                title,
            ),
            html.P(
                children=message,
                className="alert_message",
            ),
            (
                html.A(
                    link["link_text"],
                    href=link["link_href"],
                    target="_blank",
                    className="alert_link",
                )
                if link is not None
                else None
            ),
            html.Ul(
                [html.Li(i, className="alert_list_item") for i in alert_list],
                className="alert_list",
            ),
        ],
        class_name="ssb-alert",
    )


def build_input_field_section(
    metadata_fields: list[FieldTypes],
    side: str,
    variable: model.Variable,
    field_id: str = "",
) -> dbc.Form:
    """Create form with input fields for variable workspace."""
    return dbc.Form(
        [
            i.render(
                component_id={
                    "type": VARIABLES_METADATA_INPUT,
                    "variable_short_name": variable.short_name,
                    "id": i.identifier,
                },
                metadata=variable,
            )
            for i in metadata_fields
        ],
        id=f"{VARIABLES_METADATA_INPUT}-{side}-{field_id}",
        className="edit-section-form",
    )


def build_pseudo_field_section(
    metadata_fields: list[FieldTypes],
    side: str,
    pseudo_variable: model.PseudoVariable,
    field_id: str = "",
) -> dbc.Form:
    """Create form with input fields for pseudo inputs."""
    return dbc.Form(
        [
            i.render(
                component_id={
                    "type": PSEUDO_METADATA_INPUT,
                    "variable_short_name": pseudo_variable.short_name,
                    "id": i.identifier,
                },
                metadata=pseudo_variable,
            )
            for i in metadata_fields
        ],
        id=f"{PSEUDO_METADATA_INPUT}-{side}-{field_id}",
        className="edit-section-form",
    )


def build_edit_section(
    metadata_inputs: list[list[FieldTypes]],
    variable: model.Variable,
) -> html.Section:
    """Create input section for variable workspace."""
    return html.Section(
        id={"type": "edit-section"},
        children=[
            build_input_field_section(inputs, side, variable, field_id="editable")
            for inputs, side in zip(metadata_inputs, ["left", "right"], strict=False)
        ],
        className="edit-section",
    )


def build_variables_machine_section(
    metadata_inputs: list,
    title: str,
    variable: model.Variable,
) -> html.Section:
    """Create input section for variable workspace."""
    return html.Section(
        id={"type": "edit-section", "title": title},
        children=[
            ssb.Title(title, size=3, className="edit-section-title"),
            build_input_field_section(
                metadata_inputs,
                "left",
                variable,
                field_id="machine",
            ),
        ],
        className="variable-machine-section",
    )


def build_variables_pseudonymization_section(
    metadata_inputs: list,
    title: str,
    pseudo_variable: model.PseudoVariable,
) -> html.Section:
    """Create input section for pseudonymization."""
    return html.Section(
        id={"type": "edit-section", "title": title},
        children=[
            ssb.Title(title, size=3, className="edit-section-title"),
            build_pseudo_field_section(
                metadata_inputs,
                "left",
                pseudo_variable,
                field_id="pseudo",
            ),
        ],
        className="variable-section",
    )


def build_variables_pseudo_button(title: str, short_name: str) -> html.Section:
    """Create the button to add pseudonymization."""
    return html.Section(
        children=[
            ssb.Title(title, size=3, className="edit-section-title"),
            ssb.Button(
                children=["Legg til pseudonymisering"],
                id={
                    "type": "pseudo-button",
                    "short_name": short_name,
                },
                className="add-pseudo-button",
            ),
            html.Div(
                id={
                    "type": "pseudo-output",
                    "short_name": short_name,
                }
            ),
        ],
        className="variable-pseudo-button",
    )


def build_ssb_accordion(
    header: str,
    key: dict,
    variable_short_name: str,
    children: list,
) -> ssb.Accordion:
    """Build Accordion for one variable in variable workspace."""
    return ssb.Accordion(
        header=header,
        id=key,
        children=[
            html.Section(
                id={
                    "type": "variable-inputs",
                    "variable_short_name": variable_short_name,
                },
                children=children,
            ),
        ],
        className="variable-accordion",
    )


def build_dataset_machine_section(
    title: str,
    metadata_inputs: list[FieldTypes],
    dataset: model.Dataset,
    key: dict,
) -> html.Section:
    """Create section for dataset machine generated workspace."""
    return html.Section(
        id=key,
        children=[
            ssb.Title(title, size=2, className="edit-section-title"),
            dbc.Form(
                [
                    i.render(
                        component_id={
                            "type": DATASET_METADATA_INPUT,
                            "id": i.identifier,
                        },
                        metadata=dataset,
                    )
                    for i in metadata_inputs
                ],
                id=f"{DATASET_METADATA_INPUT}-{title}",
                className="edit-section-form",
            ),
        ],
        className="edit-section dataset-machine-section",
    )


def build_dataset_edit_section(
    metadata_inputs: list[list[FieldTypes]],
    dataset: model.Dataset,
    key: dict,
) -> html.Section:
    """Create edit section for dataset workspace."""
    return html.Section(
        id=key,
        children=[
            dbc.Form(
                [
                    i.render(
                        component_id={
                            "type": DATASET_METADATA_INPUT,
                            "id": i.identifier,
                        },
                        metadata=dataset,
                    )
                    for i in inputs
                ],
                id=f"{DATASET_METADATA_INPUT}-{side}",
                className="edit-section-form",
            )
            for inputs, side in zip(metadata_inputs, ["left", "right"], strict=False)
        ],
        className="edit-section dataset-edit-section",
    )


def build_link_object(text: str, href: str) -> dict | None:
    """Build link object with text and URL."""
    link_text: str | None = text
    link_href: str | None = href
    if link_text is None:
        return {"link_text": link_href, "link_href": link_href}
    if link_href is None:
        return None
    return {"link_text": link_text, "link_href": link_href}
