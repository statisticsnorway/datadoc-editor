"""Functionality common to displaying dataset and variables metadata."""

from __future__ import annotations

import logging
import urllib
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

import ssb_dash_components as ssb
from dapla_metadata.datasets import enums
from dash import html

from datadoc import state

if TYPE_CHECKING:
    from collections.abc import Callable

    from dapla_metadata.datasets import model
    from dash.development.base_component import Component
    from pydantic import BaseModel

    from datadoc.enums import LanguageStringsEnum
    from datadoc.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)

DATASET_METADATA_INPUT = "dataset-metadata-input"
DATASET_METADATA_DATE_INPUT = "dataset-metadata-date-input"
DATASET_METADATA_MULTILANGUAGE_INPUT = "dataset-metadata-multilanguage-input"

VARIABLES_METADATA_INPUT = "variables-metadata-input"
VARIABLES_METADATA_DATE_INPUT = "variables-metadata-date-input"
VARIABLES_METADATA_MULTILANGUAGE_INPUT = "dataset-metadata-multilanguage-input"

DROPDOWN_DESELECT_OPTION = "-- Velg --"

METADATA_LANGUAGES = [
    {
        "supported_language": enums.SupportedLanguages.NORSK_BOKMÅL,
        "language_title": "Bokmål",
        "language_value": "nb",
    },
    {
        "supported_language": enums.SupportedLanguages.NORSK_NYNORSK,
        "language_title": "Nynorsk",
        "language_value": "nn",
    },
    {
        "supported_language": enums.SupportedLanguages.ENGLISH,
        "language_title": "English",
        "language_value": "en",
    },
]


def get_enum_options(
    enum: type[LanguageStringsEnum],
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language."""
    dropdown_options = [
        {
            "title": i.get_value_for_language(enums.SupportedLanguages.NORSK_BOKMÅL)
            or "",
            "id": i.name,
        }
        for i in enum  # type: ignore [attr-defined]
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DESELECT_OPTION, "id": ""})
    return dropdown_options


def get_data_source_options() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = [
        {
            "title": data_sources.get_title(enums.SupportedLanguages.NORSK_BOKMÅL),
            "id": data_sources.code,
        }
        for data_sources in state.data_sources.classifications
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DESELECT_OPTION, "id": ""})
    return dropdown_options


def get_standard_metadata(metadata: BaseModel, identifier: str) -> MetadataInputTypes:
    """Get a metadata value from the model."""
    return getattr(metadata, identifier)


def get_metadata_and_stringify(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata value from the model and cast to string."""
    value = get_standard_metadata(metadata, identifier)
    if value is None:
        return ""
    return str(value)


def _get_string_type_item(
    language_strings: model.LanguageStringType,
    current_metadata_language: enums.SupportedLanguages,
) -> str | None:
    if language_strings.root is not None:
        for i in language_strings.root:
            if i.languageCode == current_metadata_language:
                return i.languageText
    return None


def get_multi_language_metadata_and_stringify(
    metadata: BaseModel,
    identifier: str,
    language: enums.SupportedLanguages,
) -> str | None:
    """Get a metadata value supporting multiple languages from the model."""
    value: model.LanguageStringType | None = getattr(metadata, identifier)
    if value is None:
        return ""
    return _get_string_type_item(value, language)


def get_comma_separated_string(metadata: BaseModel, identifier: str) -> str:
    """Get a metadata value which is a list of strings from the model and convert it to a comma separated string."""
    value: list[str] = getattr(metadata, identifier)
    try:
        return ", ".join(value)
    except TypeError:
        # This just means we got None
        return ""


@dataclass
class DisplayMetadata(ABC):
    """Controls how a given metadata field should be displayed."""

    identifier: str
    display_name: str
    description: str
    obligatory: bool = False
    editable: bool = True

    def url_encode_shortname_ids(self, component_id: dict) -> None:
        """Encodes id to hanlde non ascii values."""
        if "variable_short_name" in component_id:
            component_id["variable_short_name"] = urllib.parse.quote(
                component_id["variable_short_name"],
            )

    @abstractmethod
    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> Component:
        """Build a component."""
        ...


@dataclass
class MetadataInputField(DisplayMetadata):
    """Controls how an input field should be displayed."""

    type: str = "text"
    value_getter: Callable[[BaseModel, str], Any] = get_metadata_and_stringify

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> ssb.Input:
        """Build an Input component."""
        self.url_encode_shortname_ids(component_id)
        return ssb.Input(
            label=self.display_name,
            id=component_id,
            debounce=True,
            type=self.type,
            showDescription=True,
            description=self.description,
            readOnly=not self.editable,
            value=self.value_getter(metadata, self.identifier),
            className="input-component",
        )


@dataclass
class MetadataDropdownField(DisplayMetadata):
    """Controls how a Dropdown should be displayed."""

    options_getter: Callable[[], list[dict[str, str]]] = list

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> ssb.Dropdown:
        """Build Dropdown component."""
        self.url_encode_shortname_ids(component_id)
        return ssb.Dropdown(
            header=self.display_name,
            id=component_id,
            items=self.options_getter(),
            placeholder=DROPDOWN_DESELECT_OPTION,
            value=get_metadata_and_stringify(metadata, self.identifier),
            className="dropdown-component",
            showDescription=True,
            description=self.description,
        )


@dataclass
class MetadataDateField(DisplayMetadata):
    """Controls how fields which define a single date are displayed."""

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> ssb.Input:
        """Build Input date component."""
        self.url_encode_shortname_ids(component_id)
        return ssb.Input(
            label=self.display_name,
            id=component_id,
            debounce=False,
            type="date",
            disabled=not self.editable,
            showDescription=True,
            description=self.description,
            value=get_metadata_and_stringify(metadata, self.identifier),
            className="input-component",
        )


@dataclass
class MetadataPeriodField(DisplayMetadata):
    """Controls how fields which define a time period are displayed.

    These are a special case since two fields have a relationship to one another.
    """

    id_type: str = ""

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> ssb.Input:
        """Build Input date component."""
        component_id["type"] = self.id_type
        self.url_encode_shortname_ids(component_id)
        return ssb.Input(
            label=self.display_name,
            id=component_id,
            debounce=False,
            type="date",
            disabled=not self.editable,
            showDescription=True,
            description=self.description,
            value=get_metadata_and_stringify(metadata, self.identifier),
            className="input-component",
        )


@dataclass
class MetadataMultiLanguageField(DisplayMetadata):
    """Controls how fields which support multi-language are displayed.

    These are a special case since they return a group of input fields..
    """

    id_type: str = ""
    type: str = "text"

    def render_input_group(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> html.Section:
        """Build section with Input components for each language."""
        self.url_encode_shortname_ids(component_id)
        if "variable_short_name" in component_id:
            return html.Section(
                children=[
                    ssb.Input(
                        label=i["language_title"],
                        value=get_multi_language_metadata_and_stringify(
                            metadata,
                            self.identifier,
                            enums.SupportedLanguages(i["supported_language"]),
                        ),
                        debounce=True,
                        id={
                            "type": self.id_type,
                            "id": component_id["id"],
                            "variable_short_name": component_id["variable_short_name"],
                            "language": i["language_value"],
                        },
                        type=self.type,
                        className="multilanguage-input-component",
                    )
                    for i in METADATA_LANGUAGES
                ],
            )
        return html.Section(
            children=[
                ssb.Input(
                    label=i["language_title"],
                    value=get_multi_language_metadata_and_stringify(
                        metadata,
                        self.identifier,
                        enums.SupportedLanguages(i["supported_language"]),
                    ),
                    debounce=True,
                    id={
                        "type": self.id_type,
                        "id": component_id["id"],
                        "language": i["language_value"],
                    },
                    type=self.type,
                    className="multilanguage-input-component",
                )
                for i in METADATA_LANGUAGES
            ],
        )

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> html.Fieldset:
        """Build fieldset group."""
        return html.Fieldset(
            children=(
                [
                    ssb.Glossary(
                        children=(
                            html.Legend(
                                self.display_name,
                                className="multilanguage-legend",
                            )
                        ),
                        explanation=self.description,
                        className="legend-glossary",
                    ),
                    self.render_input_group(
                        component_id=component_id,
                        metadata=metadata,
                    ),
                ]
            ),
            className="multilanguage-fieldset",
        )


@dataclass
class MetadataCheckboxField(DisplayMetadata):
    """Controls for how a checkbox metadata field should be displayed."""

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> ssb.Checkbox:
        """Build Checkbox component."""
        self.url_encode_shortname_ids(component_id)
        return ssb.Checkbox(
            label=self.display_name,
            id=component_id,
            disabled=not self.editable,
            value=get_standard_metadata(metadata, self.identifier),
            showDescription=True,
            description=self.description,
            className="metadata-checkbox-field",
        )


FieldTypes = (
    MetadataInputField
    | MetadataDropdownField
    | MetadataDateField
    | MetadataCheckboxField
    | MetadataPeriodField
    | MetadataMultiLanguageField
)
