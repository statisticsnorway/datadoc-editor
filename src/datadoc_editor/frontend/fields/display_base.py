"""Functionality common to displaying dataset and variables metadata."""

from __future__ import annotations

import logging
import urllib
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

import ssb_dash_components as ssb
from dapla_metadata.datasets import enums
from dapla_metadata.datasets import model
from dapla_metadata.datasets.utility.urn import ReferenceUrlTypes
from dapla_metadata.datasets.utility.urn import UrnConverter
from dash import dcc
from dash import html

from datadoc_editor import state
from datadoc_editor.frontend.components.identifiers import ADD_USE_RESTRICTION_BUTTON
from datadoc_editor.frontend.components.identifiers import FORCE_RERENDER_COUNTER
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_ID_STORE
from datadoc_editor.frontend.components.identifiers import (
    USE_RESTRICTION_LIST_CONTAINER,
)
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_OPTION_STORE
from datadoc_editor.frontend.components.identifiers import USE_RESTRICTION_STORE
from datadoc_editor.frontend.constants import DELETE_SELECTED
from datadoc_editor.frontend.constants import DESELECT
from datadoc_editor.frontend.constants import DROPDOWN_DELETE_OPTION
from datadoc_editor.frontend.constants import DROPDOWN_DESELECT_OPTION

if TYPE_CHECKING:
    from collections.abc import Callable

    from dash.development.base_component import Component
    from pydantic import BaseModel

    from datadoc_editor.enums import LanguageStringsEnum
    from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes

logger = logging.getLogger(__name__)

DATASET_METADATA_INPUT = "dataset-metadata-input"
DATASET_METADATA_DATE_INPUT = "dataset-metadata-date-input"
DATASET_METADATA_MULTILANGUAGE_INPUT = "dataset-metadata-multilanguage-input"
DATASET_METADATA_MULTIDROPDOWN_INPUT = "dataset-metadata-multidropdown-input"

PSEUDO_METADATA_INPUT = "pseudo-metadata-input"
VARIABLES_METADATA_INPUT = "variables-metadata-input"
VARIABLES_METADATA_DATE_INPUT = "variables-metadata-date-input"
VARIABLES_METADATA_MULTILANGUAGE_INPUT = "dataset-metadata-multilanguage-input"


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


def get_enum_options_with_delete_option(
    enum: type[LanguageStringsEnum],
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language with delete option."""
    dropdown_options = get_enum_options(enum)
    dropdown_options.insert(0, {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED})
    return dropdown_options


def get_enum_options_with_delete_and_deselect_option(
    enum: type[LanguageStringsEnum],
) -> list[dict[str, str]]:
    """Generate the list of options based on the currently chosen language with delete and deselect."""
    dropdown_options = get_enum_options(enum)
    dropdown_options[0] = {"title": DROPDOWN_DESELECT_OPTION, "id": DESELECT}
    dropdown_options.insert(1, {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED})
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


def get_data_source_options_with_delete() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = get_data_source_options()
    dropdown_options[0] = {"title": DROPDOWN_DESELECT_OPTION, "id": DESELECT}
    dropdown_options.insert(1, {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED})
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
    obligatory: bool
    editable: bool

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
            required=self.obligatory and self.editable,
        )


@dataclass
class MetadataUrnField(DisplayMetadata):
    """Controls how a URN input field should be displayed."""

    converter: UrnConverter

    def url_getter(self, metadata: BaseModel, field_name: str) -> str | None:
        """Get a URL for a URN field, if possible. Falls back to the raw value."""
        if resource_id := self.converter.get_id(
            str(get_metadata_and_stringify(metadata, field_name))
        ):
            return self.converter.get_url(
                str(resource_id),
                url_type=ReferenceUrlTypes.FRONTEND,
                visibility="public",
            )
        return get_metadata_and_stringify(metadata, field_name)

    def value_setter(self, value: str) -> str:
        """Validate and convert an ID to a URN.

        Args:
            value (str): The value from user input.

        Raises:
            ValueError: If the value is not a valid ID.

        Returns:
            str: The full URN.
        """
        if not self.converter.is_id(value):
            msg = f"Value '{value}' is not a valid ID"
            raise ValueError(msg)
        return self.converter.get_urn(value)

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> html.Section:
        """Build a URN Field."""
        self.url_encode_shortname_ids(component_id)
        value = self.url_getter(metadata, self.identifier)
        section_id = component_id.copy()
        section_id["type"] = VARIABLES_METADATA_INPUT + "-urn-section"
        section = html.Section(
            id=section_id,
            children=[
                ssb.Input(
                    label=self.display_name,
                    id=component_id,
                    debounce=True,
                    type="text",
                    showDescription=True,
                    description=self.description,
                    readOnly=not self.editable,
                    value=self.converter.get_id(
                        value or ""
                    ),  # Present the Identifier for editing
                    className="input-component",
                    required=self.obligatory and self.editable,
                ),
            ],
        )
        if value:
            section.children.append(
                ssb.Link(
                    "Vis i datakatalogen (kommer!)",
                    icon=html.I(className="bi bi-arrow-right"),
                    href=value,
                    isExternal=True,
                )
            )
        return section


@dataclass
class MetadataDropdownField(DisplayMetadata):
    """Controls how a Dropdown should be displayed."""

    options_getter: Callable[[], list[dict[str, str]]] = list
    searchable: bool = False

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
            required=self.obligatory and self.editable,
            searchable=self.searchable,
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
            required=self.obligatory and self.editable,
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
                            ),
                            ssb.RequiredAsterisk()
                            if self.obligatory and self.editable
                            else None,
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
class MetadataMultiDropdownField(DisplayMetadata):
    """Controls how fields which support multi-dropdown values are displayed.

    These are a special case since they return a group of both dropdown and date fields.
    This current version is only compatible with the use restriction field.
    """

    id_type: str = ""
    type: str = "text"
    options_getter: Callable[[], list[dict[str, str]]] = list
    type_display_name: str = ""
    date_display_name: str = ""
    type_description: str = ""
    date_description: str = ""

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> html.Fieldset:
        """Build fieldset group."""
        use_restrictions: list[model.UseRestrictionItem] = cast(
            "list[model.UseRestrictionItem]",
            get_standard_metadata(metadata, self.identifier) or [],
        )
        initial_data = [
            {
                "use_restriction_type": i.use_restriction_type,
                "use_restriction_date": i.use_restriction_date,
            }
            for i in use_restrictions
        ]

        idx = {"type": self.id_type, "id": component_id["id"]}

        children = [
            ssb.Glossary(
                children=[
                    html.Legend(self.display_name, className="multilanguage-legend")
                ],
                explanation=self.description,
                className="legend-glossary",
            ),
            html.Div(id=USE_RESTRICTION_LIST_CONTAINER),
            dcc.Store(id=USE_RESTRICTION_STORE, data=initial_data),
            dcc.Store(id=USE_RESTRICTION_OPTION_STORE, data=self.options_getter()),
            dcc.Store(id=USE_RESTRICTION_ID_STORE, data=idx),
            dcc.Store(id=FORCE_RERENDER_COUNTER, data=0),
            ssb.Button("Legg til bruksrestriksjon", id=ADD_USE_RESTRICTION_BUTTON),
        ]

        return html.Fieldset(children=children, className="multidropdown-fieldset")


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
            required=self.obligatory and self.editable,
        )


FieldTypes = (
    MetadataInputField
    | MetadataUrnField
    | MetadataDropdownField
    | MetadataCheckboxField
    | MetadataPeriodField
    | MetadataMultiLanguageField
    | MetadataMultiDropdownField
)
