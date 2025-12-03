"""Factory functions for different components are defined here."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import ssb_dash_components as ssb
from dash import html

from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.constants import PSEUDONYMIZATION
from datadoc_editor.frontend.fields.display_base import DATASET_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_base import PSEUDO_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import VARIABLES_METADATA_INPUT
from datadoc_editor.frontend.fields.display_base import FieldTypes
from datadoc_editor.frontend.fields.display_base import (
    get_enum_options_with_delete_option,
)

if TYPE_CHECKING:
    from dapla_metadata.datasets import model
    from dapla_metadata.datasets.utility.utils import VariableType
    from datadoc_model.required import model as required_model


class AlertTypes(Enum):
    """Types of alerts."""

    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    INFO = auto()


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
    AlertTypes.INFO: AlertType(
        color="info",
    ),
}


def build_ssb_alert(  # noqa: PLR0913
    alert_type: AlertTypes,
    title: str,
    message: str | None = None,
    link: dict | None = None,
    alert_list: list | None = None,
    *,
    is_dissmissable: bool | None = True,
) -> dbc.Alert:
    """Make a Dash Alert according to SSBs Design System."""
    alert = AlertType.get_type(alert_type)
    if alert_list is None:
        alert_list = []
    return dbc.Alert(
        is_open=True,
        dismissable=is_dissmissable,
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
    variable: VariableType,
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
        key=str(uuid.uuid4()),
        className="edit-section-form",
    )


def build_pseudo_field_section(
    metadata_fields: list[FieldTypes],
    side: str,
    variable: VariableType,
    pseudonymization: model.Pseudonymization | required_model.Pseudonymization,
    field_id: str = "",
) -> dbc.Form:
    """Create form with input fields for pseudo inputs."""
    return dbc.Form(
        [
            i.render(
                component_id={
                    "type": PSEUDO_METADATA_INPUT,
                    "variable_short_name": variable.short_name,
                    "id": i.identifier,
                },
                metadata=pseudonymization,
            )
            for i in metadata_fields
        ],
        id=f"{PSEUDO_METADATA_INPUT}-{side}-{field_id}",
        key=str(uuid.uuid4()),
        className="edit-section-form",
    )


def build_edit_section(
    metadata_inputs: list[list[FieldTypes]],
    variable: VariableType,
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
    variable: VariableType,
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
    title: str,
    variable: VariableType,
    selected_algorithm: PseudonymizationAlgorithmsEnum | None,
) -> html.Section:
    """Create input section for pseudonymization with dropdown for selecting pseudo algorithm."""
    return html.Section(
        id={"type": "edit-section", "title": title},
        children=[
            ssb.Title(title, size=3, className="edit-section-title"),
            ssb.Dropdown(
                header=PSEUDONYMIZATION,
                placeholder=DROPDOWN_DESELECT_OPTION,
                showDescription=False,
                description="",
                id={
                    "type": "pseudonymization-dropdown",
                    "variable": variable.short_name,
                },
                items=get_enum_options_with_delete_option(
                    PseudonymizationAlgorithmsEnum
                ),
                value=selected_algorithm.value if selected_algorithm else None,
            ),
            html.Div(
                id={"type": "pseudo-field-container", "variable": variable.short_name}
            ),
        ],
        className="variable-section",
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
