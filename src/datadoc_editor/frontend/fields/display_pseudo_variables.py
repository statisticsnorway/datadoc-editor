from enum import Enum

import arrow
from pydantic import BaseModel

from datadoc_editor.frontend.fields.display_base import FieldTypes
from datadoc_editor.frontend.fields.display_base import MetadataInputField
from datadoc_editor.frontend.fields.display_base import get_standard_metadata


class PseudoVariableIdentifiers(str, Enum):
    """Pseudo fields."""

    PSEUDONYMIZATION_TIME = "pseudonymization_time"
    STABLE_IDENTIFIER_TYPE = "stable_identifier_type"
    STABLE_IDENTIFIER_VERSION = "stable_identifier_version"
    ENCRYPTION_ALGORITHM = "encryption_algorithm"
    ENCRYPTION_KEY_REFERENCE = "encryption_key_reference"
    ENCRYPTION_ALGORITHM_PARAMETERS = "encryption_algorithm_parameters"


def get_datetime_and_stringify(metadata: BaseModel, identifier: str) -> str | None:
    """Get a metadata datetime value from the model and cast date to string."""
    value = get_standard_metadata(metadata, identifier)
    if not value:
        return ""
    return arrow.get(str(value)).format("YYYY-MM-DD")


PSEUDO_FIELDS: dict[
    PseudoVariableIdentifiers,
    FieldTypes,
] = {
    PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME: MetadataInputField(
        identifier=PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME.value,
        display_name="Pseudonymiseringstidspunkt",
        description="Tidspunktet datasettet ble pseudonymisert.",
        type="date",
        obligatory=False,
        editable=True,
        value_getter=get_datetime_and_stringify,
    ),
    PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION: MetadataInputField(
        identifier=PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION.value,
        display_name="Stabil identifikator versjon",
        description="Det skal brukes den type versjonering som er brukt for stabil identifikator katalogen, eksempler kan være dato eller semantisk versjonering.",
        type="date",
        obligatory=False,
        editable=True,
        value_getter=get_datetime_and_stringify,
    ),
    PseudoVariableIdentifiers.STABLE_IDENTIFIER_TYPE: MetadataInputField(
        identifier=PseudoVariableIdentifiers.STABLE_IDENTIFIER_TYPE.value,
        display_name="Stabil identifikator type",
        description="Type stabil identifikator som er benyttet før pseudonymisering (kryptering), eksempelvis at fødselsnummer er byttet ut med SNR fra SNR-katalogen i FREG.",
        obligatory=False,
        editable=True,
    ),
    PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM: MetadataInputField(
        identifier=PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM.value,
        display_name="Krypteringsalgoritme",
        description="Krypteringsalgoritmen som er benyttet for å pseudonymisere variabelen.",
        obligatory=True,
        editable=True,
    ),
    PseudoVariableIdentifiers.ENCRYPTION_KEY_REFERENCE: MetadataInputField(
        identifier=PseudoVariableIdentifiers.ENCRYPTION_KEY_REFERENCE.value,
        display_name="Krypteringsnøkkel referanse",
        description="Navn eller referanse til krypteringsnøkkelen som er benyttet til å pseudonymisere variabelen.",
        obligatory=True,
        editable=True,
    ),
    PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM_PARAMETERS: MetadataInputField(
        identifier=PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM_PARAMETERS.value,
        display_name="Krypteringsalgoritme-parametere",
        description="Eventuelle krypteringsalgoritme-parametere som er benyttet utover “encryption_key_reference” nevnt over.",
        obligatory=False,
        editable=False,
    ),
}

PSEUDONYMIZATION_METADATA = [m for m in PSEUDO_FIELDS.values() if m.editable]
PSEUDONYMIZATION_PAPIS_WITH_STABLE_ID_METADATA = [
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
PSEUDONYMIZATION_PAPIS_WITHOUT_STABLE_ID_METADATA = [
    m
    for m in PSEUDO_FIELDS.values()
    if (
        m.identifier in (PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME.value)
        and m.editable
    )
]
PSEUDONYMIZATION_DEAD_METADATA = [
    m
    for m in PSEUDO_FIELDS.values()
    if (
        m.identifier in (PseudoVariableIdentifiers.PSEUDONYMIZATION_TIME.value)
        and m.editable
    )
]

OBLIGATORY_VARIABLES_METADATA_PSEUDO_IDENTIFIERS_AND_DISPLAY_NAME: list[tuple] = [
    (m.identifier, m.display_name) for m in PSEUDO_FIELDS.values() if m.obligatory
]
