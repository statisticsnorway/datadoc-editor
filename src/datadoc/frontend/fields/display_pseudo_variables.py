from enum import Enum

from datadoc.frontend.fields.display_base import FieldTypes
from datadoc.frontend.fields.display_base import MetadataInputField


class PseudonymizationIdentifiers(str, Enum):
    """Pseudo fileds."""

    SHORT_NAME = "short_name"
    DATA_ELEMENT_PATH = "data_element_path"
    DATA_ELEMENT_PATTERN = "data_element_pattern"
    STABLE_IDENTIFIER_TYPE = "stable_identifier_type"
    STABLE_IDENTIFIER_VERSION = "stable_identifier_version"
    ENCRYPTION_ALGORITHM = "encryption_algorithm"
    ENCRYPTION_KEY_REFERENCE = "encryption_key_reference"
    ENCRYPTION_ALGORITHM_PARAMETERS = "encryption_algorithm_parameters"
    SOURCE_VARIABLE = "source_variable"
    SOURCE_DISPLAY_DATATYPE = "source_variable_datatype"


PSEUDO_FIELDS: dict[
    PseudonymizationIdentifiers,
    FieldTypes,
] = {
    PseudonymizationIdentifiers.SHORT_NAME: MetadataInputField(
        identifier=PseudonymizationIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen (elementet) i datasettet som er pseudonymisert",
        obligatory=True,
        editable=False,
    ),
    PseudonymizationIdentifiers.DATA_ELEMENT_PATH: MetadataInputField(
        identifier=PseudonymizationIdentifiers.DATA_ELEMENT_PATH.value,
        display_name="Dataelement sti",
        description="Sti (path) til den pseudonymiserte variabelen (elementet) i et hierarkisk datasett.",
        obligatory=True,
    ),
    PseudonymizationIdentifiers.DATA_ELEMENT_PATTERN: MetadataInputField(
        identifier=PseudonymizationIdentifiers.DATA_ELEMENT_PATTERN.value,
        display_name="Dataelement mønster",
        description="Eventuelt “søke-mønster” (glob pattern) som resulterte i at denne variabelen ble pseudonymisert.",
        obligatory=True,
    ),
    PseudonymizationIdentifiers.STABLE_IDENTIFIER_VERSION: MetadataInputField(
        identifier=PseudonymizationIdentifiers.STABLE_IDENTIFIER_VERSION.value,
        display_name="Stabil identifikator type",
        description="Type stabil identifikator som er benyttet før pseudonymisering (krypteirng), eksempelvis at fødselsnummer er byttet ut med SNR fra SNR-katalogen i FREG.",
        obligatory=True,
    ),
    PseudonymizationIdentifiers.STABLE_IDENTIFIER_TYPE: MetadataInputField(
        identifier=PseudonymizationIdentifiers.STABLE_IDENTIFIER_TYPE.value,
        display_name="Stabil identifikator versjon",
        description="Det skal brukes den type versjonering som er brukt for stabil identifikator katalogen, eksempler kan være dato eller semantisk versjonering.",
        obligatory=True,
    ),
    PseudonymizationIdentifiers.ENCRYPTION_ALGORITHM: MetadataInputField(
        identifier=PseudonymizationIdentifiers.ENCRYPTION_ALGORITHM.value,
        display_name="Krypteringsalgoritme",
        description="Krypteringsalgoritmen som er benyttet for å pseudonymisere variabelen.",
        obligatory=True,
    ),
    PseudonymizationIdentifiers.ENCRYPTION_KEY_REFERENCE: MetadataInputField(
        identifier=PseudonymizationIdentifiers.ENCRYPTION_KEY_REFERENCE.value,
        display_name="Krypteringsnøkkel referanse",
        description="Navn eller referanse til krypteringsnøkkelen som er benyttet til å pseudonymisere variabelen.",
        obligatory=True,
    ),
    PseudonymizationIdentifiers.ENCRYPTION_ALGORITHM_PARAMETERS: MetadataInputField(
        identifier=PseudonymizationIdentifiers.ENCRYPTION_ALGORITHM_PARAMETERS.value,
        display_name="Krypteringsalgoritme-parametere",
        description="Eventuelle krypteringsalgoritme-parametere som er benyttet utover “encryption_key_reference” nevnt over.",
        obligatory=True,
        editable=False,
    ),
    PseudonymizationIdentifiers.SOURCE_VARIABLE: MetadataInputField(
        identifier=PseudonymizationIdentifiers.SOURCE_VARIABLE.value,
        display_name="Kilde-variabel",
        description="Eventuelt navn på kilde-variabelen før pseudonymisering.",
        obligatory=True,
    ),
    PseudonymizationIdentifiers.SOURCE_DISPLAY_DATATYPE: MetadataInputField(
        identifier=PseudonymizationIdentifiers.SOURCE_DISPLAY_DATATYPE.value,
        display_name="Kilde-variabel datatype",
        description="Eventuell datatype på kildevariabelen før pseudonymisering.",
        obligatory=True,
    ),
}

PSEUDONYMIZATION_METADATA = list(PSEUDO_FIELDS.values())
