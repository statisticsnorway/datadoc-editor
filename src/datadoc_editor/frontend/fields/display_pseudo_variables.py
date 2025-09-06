import functools
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import ssb_dash_components as ssb
from dash import html
from pydantic import BaseModel

from datadoc_editor.enums import PseudonymizationAlgorithms
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_base import DisplayMetadata
from datadoc_editor.frontend.fields.display_base import FieldTypes
from datadoc_editor.frontend.fields.display_base import MetadataDateField
from datadoc_editor.frontend.fields.display_base import MetadataInputField
from datadoc_editor.frontend.fields.display_base import get_enum_options
from datadoc_editor.frontend.fields.display_base import get_metadata_and_stringify


class PseudoVariableIdentifiers(str, Enum):
    """Pseudo fields."""

    PSEUDONYMIZATION_TIME = "pseudonymization_time"
    STABLE_IDENTIFIER_TYPE = "stable_identifier_type"
    STABLE_IDENTIFIER_VERSION = "stable_identifier_version"
    ENCRYPTION_ALGORITHM = "encryption_algorithm"
    ENCRYPTION_KEY_REFERENCE = "encryption_key_reference"
    ENCRYPTION_ALGORITHM_PARAMETERS = "encryption_algorithm_parameters"


@dataclass
class PseudoField(DisplayMetadata):
    """Controls how a pseudo section should be displayed."""

    options_getter: Callable[[], list[dict[str, str]]] = list

    def render(
        self,
        component_id: dict,
        metadata: BaseModel,
    ) -> html.Section:
        """Build Pseudo component."""
        self.url_encode_shortname_ids(component_id)
        return html.Section(
            [
                ssb.Dropdown(
                    header=self.display_name,
                    id=component_id,
                    items=self.options_getter(),
                    placeholder=DROPDOWN_DESELECT_OPTION,
                    value=get_metadata_and_stringify(metadata, self.identifier),
                    className="dropdown-component",
                    showDescription=False,
                    description=self.description,
                )
            ]
        )


class PseudoIdentifier(str, Enum):
    """Identifier for pseudonymization."""

    PSEDONYMIZATION = "Pseudonymisert"

    DISPLAY_PSEUDO = PseudoField(
        identifier=PSEDONYMIZATION,
        display_name="Pseudonymisert",
        description="",
        options_getter=functools.partial(
            get_enum_options,
            PseudonymizationAlgorithms,
        ),
    )


PSEUDO_FIELDS: dict[
    PseudoVariableIdentifiers,
    FieldTypes,
] = {
    PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME: MetadataDateField(
        identifier=PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME.value,
        display_name="Pseudonymiseringstidspunkt",
        description="Tidspunktet datasettet ble pseudonymisert.",
        obligatory=True,
    ),
    PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION: MetadataInputField(
        identifier=PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION.value,
        display_name="Stabil identifikator type",
        description="Type stabil identifikator som er benyttet før pseudonymisering (krypteirng), eksempelvis at fødselsnummer er byttet ut med SNR fra SNR-katalogen i FREG.",
        obligatory=True,
    ),
    PseudoVariableIdentifiers.STABLE_IDENTIFIER_TYPE: MetadataInputField(
        identifier=PseudoVariableIdentifiers.STABLE_IDENTIFIER_TYPE.value,
        display_name="Stabil identifikator versjon",
        description="Det skal brukes den type versjonering som er brukt for stabil identifikator katalogen, eksempler kan være dato eller semantisk versjonering.",
        obligatory=True,
    ),
    PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM: MetadataInputField(
        identifier=PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM.value,
        display_name="Krypteringsalgoritme",
        description="Krypteringsalgoritmen som er benyttet for å pseudonymisere variabelen.",
        obligatory=True,
    ),
    PseudoVariableIdentifiers.ENCRYPTION_KEY_REFERENCE: MetadataInputField(
        identifier=PseudoVariableIdentifiers.ENCRYPTION_KEY_REFERENCE.value,
        display_name="Krypteringsnøkkel referanse",
        description="Navn eller referanse til krypteringsnøkkelen som er benyttet til å pseudonymisere variabelen.",
        obligatory=True,
    ),
    PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM_PARAMETERS: MetadataInputField(
        identifier=PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM_PARAMETERS.value,
        display_name="Krypteringsalgoritme-parametere",
        description="Eventuelle krypteringsalgoritme-parametere som er benyttet utover “encryption_key_reference” nevnt over.",
        obligatory=True,
        editable=False,
    ),
}

PSEUDONYMIZATION_METADATA = list(PSEUDO_FIELDS.values())
PSEUDONYMIZATION_PAPIS_WITH_STABILE_ID = [
    m
    for m in PSEUDO_FIELDS.values()
    if (
        m.identifier
        in (
            PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME.value,
            PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION.value,
        )
        and m.editable
    )
]
PSEUDONYMIZATION_PAPIS_WITHOUT_STABILE_ID = [
    m
    for m in PSEUDO_FIELDS.values()
    if (
        m.identifier in (PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME.value)
        and m.editable
    )
]
PSEUDONYMIZATION_DEAD = [
    m
    for m in PSEUDO_FIELDS.values()
    if (
        m.identifier
        in (
            PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME.value,
            PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION.value,
        )
        and m.editable
    )
]
