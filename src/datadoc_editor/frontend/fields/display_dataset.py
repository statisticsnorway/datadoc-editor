"""Functionality for displaying dataset metadata."""

from __future__ import annotations

import functools
import logging
from enum import Enum

from dapla_metadata.datasets import enums

from datadoc_editor import state
from datadoc_editor.enums import Assessment
from datadoc_editor.enums import DataSetState
from datadoc_editor.enums import DataSetStatus
from datadoc_editor.enums import UseRestrictionType
from datadoc_editor.frontend.fields.display_base import DATASET_METADATA_DATE_INPUT
from datadoc_editor.frontend.fields.display_base import (
    DATASET_METADATA_MULTIDROPDOWN_INPUT,
)
from datadoc_editor.frontend.fields.display_base import (
    DATASET_METADATA_MULTILANGUAGE_INPUT,
)
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_base import FieldTypes
from datadoc_editor.frontend.fields.display_base import MetadataDropdownField
from datadoc_editor.frontend.fields.display_base import MetadataInputField
from datadoc_editor.frontend.fields.display_base import MetadataMultiDropdownField
from datadoc_editor.frontend.fields.display_base import MetadataMultiLanguageField
from datadoc_editor.frontend.fields.display_base import MetadataPeriodField
from datadoc_editor.frontend.fields.display_base import get_comma_separated_string
from datadoc_editor.frontend.fields.display_base import get_enum_options

logger = logging.getLogger(__name__)


def get_statistical_subject_options() -> list[dict[str, str]]:
    """Generate the list of options for statistical subject."""
    dropdown_options = [
        {
            "title": f"{primary.get_title(enums.SupportedLanguages.NORSK_BOKMÅL)} - {secondary.get_title(enums.SupportedLanguages.NORSK_BOKMÅL)}",
            "id": secondary.subject_code,
        }
        for primary in state.statistic_subject_mapping.primary_subjects
        for secondary in primary.secondary_subjects
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DESELECT_OPTION, "id": ""})
    return dropdown_options


def get_owner_options() -> list[dict[str, str]]:
    """Collect the owner options."""
    dropdown_options = [
        {
            "title": f"{option.code} - {option.get_title(enums.SupportedLanguages.NORSK_BOKMÅL)}",
            "id": option.code,
        }
        for option in state.organisational_units.classifications
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DESELECT_OPTION, "id": ""})
    return dropdown_options


class DatasetIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/l/c/aoSfEWJU."""

    SHORT_NAME = "short_name"
    ASSESSMENT = "assessment"
    DATASET_STATUS = "dataset_status"
    DATASET_STATE = "dataset_state"
    NAME = "name"
    DESCRIPTION = "description"
    POPULATION_DESCRIPTION = "population_description"
    VERSION = "version"
    VERSION_DESCRIPTION = "version_description"
    SUBJECT_FIELD = "subject_field"
    KEYWORD = "keyword"
    SPATIAL_COVERAGE_DESCRIPTION = "spatial_coverage_description"
    USE_RESTRICTIONS = "use_restrictions"
    ID = "id"
    OWNER = "owner"
    FILE_PATH = "file_path"
    METADATA_CREATED_DATE = "metadata_created_date"
    METADATA_CREATED_BY = "metadata_created_by"
    METADATA_LAST_UPDATED_DATE = "metadata_last_updated_date"
    METADATA_LAST_UPDATED_BY = "metadata_last_updated_by"
    CONTAINS_DATA_FROM = "contains_data_from"
    CONTAINS_DATA_UNTIL = "contains_data_until"


DISPLAY_DATASET: dict[
    DatasetIdentifiers,
    FieldTypes,
] = {
    DatasetIdentifiers.NAME: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.NAME.value,
        display_name="Navn",
        description="Oppgi navn på datasettet. Navnet skal være forståelig for mennesker slik at det er søkbart.",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.DESCRIPTION.value,
        display_name="Beskrivelse",
        description="Beskrivelse av datasettet",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.ASSESSMENT: MetadataDropdownField(
        identifier=DatasetIdentifiers.ASSESSMENT.value,
        display_name="Verdivurdering",
        description="Verdivurderingen utledes fra datatilstanden og kan ha verdiene: sensitiv (kildedata), skjermet (inndata, klargjorte data og statistikk) og åpen (utdata).",
        obligatory=True,
        editable=True,
        options_getter=functools.partial(
            get_enum_options,
            Assessment,
        ),
    ),
    DatasetIdentifiers.POPULATION_DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjon",
        description='Oppgi populasjonen datasettet dekker. Beskrivelsen skal inkludere enhetstype, geografisk dekningsområde og tidsperiode, f.eks.  "Personer bosatt  i Norge 1990-2020"',
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.USE_RESTRICTIONS: MetadataMultiDropdownField(
        identifier=DatasetIdentifiers.USE_RESTRICTIONS.value,
        display_name="Bruksrestriksjon",
        description="Velg hvilken bruksrestriksjon som gjelder.",
        obligatory=False,
        editable=True,
        options_getter=functools.partial(get_enum_options, UseRestrictionType),
        type_display_name="Bruksrestriksjon",
        type_description="Oppgi om det er knyttet noen bruksrestriksjoner til datasettet, f.eks. krav om sletting/anonymisering.",
        date_display_name="Dato for restriksjon",
        date_description='Oppgi ev. "tiltaksdato" for bruksrestriksjoner, f.eks. frist for sletting/anonymisering. Noen bruksrestriksjoner vil ikke ha en slik dato, f.eks. vil en behandlingsbegrensning normalt være permanent/tidsuavhengig.',
        id_type=DATASET_METADATA_MULTIDROPDOWN_INPUT,
    ),
    DatasetIdentifiers.DATASET_STATE: MetadataDropdownField(
        identifier=DatasetIdentifiers.DATASET_STATE.value,
        display_name="Datatilstand",
        description="Datasettets datatilstand der en av de følgende er mulige: kildedata, inndata, klargjorte data, statistikk og utdata.",
        obligatory=True,
        editable=True,
        options_getter=functools.partial(
            get_enum_options,
            DataSetState,
        ),
    ),
    DatasetIdentifiers.DATASET_STATUS: MetadataDropdownField(
        identifier=DatasetIdentifiers.DATASET_STATUS.value,
        display_name="Status",
        description="Oppgi om metadataene er under arbeid (utkast), kan deles internt (intern), kan deles eksternt(ekstern) eller er avsluttet/erstattet (utgått). Det kan være restriksjoner knyttet til deling både internt og eksternt.",
        obligatory=True,
        editable=True,
        options_getter=functools.partial(
            get_enum_options,
            DataSetStatus,
        ),
    ),
    DatasetIdentifiers.CONTAINS_DATA_FROM: MetadataPeriodField(
        identifier=DatasetIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Oppgi hvilken dato datasettet inneholder data f.o.m. ÅÅÅÅ-MM-DD",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_DATE_INPUT,
    ),
    DatasetIdentifiers.CONTAINS_DATA_UNTIL: MetadataPeriodField(
        identifier=DatasetIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="Oppgi hvilken dato datasettet inneholder data t.o.m. ÅÅÅÅ-MM-DD",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_DATE_INPUT,
    ),
    DatasetIdentifiers.SUBJECT_FIELD: MetadataDropdownField(
        identifier=DatasetIdentifiers.SUBJECT_FIELD.value,
        display_name="Statistikkområde",
        description="Oppgi det primære statistikkområdet som datasettet tilhører.",
        obligatory=True,
        editable=True,
        searchable=True,
        options_getter=get_statistical_subject_options,
    ),
    DatasetIdentifiers.KEYWORD: MetadataInputField(
        identifier=DatasetIdentifiers.KEYWORD.value,
        display_name="Nøkkelord",
        description="Her kan en oppgi nøkkelord som beskriver datasettet, og som kan brukes i søk. Nøkkelordene må legges inn som en kommaseparert streng. F.eks. befolkning, skatt, arbeidsledighet",
        obligatory=False,
        editable=True,
        value_getter=get_comma_separated_string,
    ),
    DatasetIdentifiers.VERSION: MetadataInputField(
        identifier=DatasetIdentifiers.VERSION.value,
        display_name="Versjon",
        description="Oppgi hvilken versjon av datasettet dette er (versjonering av datasett er beskrevet i Dapla-manualen).",
        obligatory=True,
        editable=True,
        type="number",
    ),
    DatasetIdentifiers.VERSION_DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.VERSION_DESCRIPTION.value,
        display_name="Versjonsbeskrivelse",
        description="Beskriv kort årsaken til at denne versjonen av datasettet ble laget.",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION: MetadataMultiLanguageField(
        identifier=DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION.value,
        display_name="Geografisk dekningsområde",
        description="Oppgi datasettets geografiske dekningsområde, f.eks. Norge.",
        obligatory=True,
        editable=True,
        id_type=DATASET_METADATA_MULTILANGUAGE_INPUT,
    ),
    DatasetIdentifiers.SHORT_NAME: MetadataInputField(
        identifier=DatasetIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Datasettets tekniske kortnavn (uten versjonsnummer og filendelse).",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.ID: MetadataInputField(
        identifier=DatasetIdentifiers.ID.value,
        display_name="ID",
        description="Den unike SSB-identifikatoren for datasettet.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.FILE_PATH: MetadataInputField(
        identifier=DatasetIdentifiers.FILE_PATH.value,
        display_name="Filsti",
        description="Filstien inneholder datasettets kortnavn og stien til stedet der det er lagret.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_DATE: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_CREATED_DATE.value,
        display_name="Dato opprettet",
        description="Datoen metadataene for datasettet ble opprettet",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_CREATED_BY: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_CREATED_BY.value,
        display_name="Opprettet av",
        description=" Navnet på personen som opprettet metadataene",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_DATE: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_DATE.value,
        display_name="Dato oppdatert",
        description="Datoen metadataene om datasettet sist ble oppdatert",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.METADATA_LAST_UPDATED_BY: MetadataInputField(
        identifier=DatasetIdentifiers.METADATA_LAST_UPDATED_BY.value,
        display_name="Oppdatert av",
        description="Navnet på personen som sist oppdaterte metadataene.",
        obligatory=True,
        editable=False,
    ),
    DatasetIdentifiers.OWNER: MetadataInputField(
        identifier=DatasetIdentifiers.OWNER.value,
        display_name="Eier",
        description="Navnet på teamet som eier datasettet",
        obligatory=True,
        editable=False,
    ),
}

MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS = [
    m.identifier
    for m in DISPLAY_DATASET.values()
    if isinstance(m, MetadataMultiLanguageField)
]

MULTIPLE_DROPDOWN_DATASET_IDENTIFIERS = [
    m.identifier
    for m in DISPLAY_DATASET.values()
    if isinstance(m, MetadataMultiDropdownField)
]

EDITABLE_DATASET_METADATA_LEFT = [
    m
    for m in DISPLAY_DATASET.values()
    if m.editable and isinstance(m, MetadataMultiLanguageField)
]

EDITABLE_DATASET_METADATA_LEFT.insert(3, DISPLAY_DATASET[DatasetIdentifiers.VERSION])


EDITABLE_DATASET_METADATA_RIGHT = [
    m
    for m in DISPLAY_DATASET.values()
    if m.editable and m not in EDITABLE_DATASET_METADATA_LEFT
]


NON_EDITABLE_DATASET_METADATA = [m for m in DISPLAY_DATASET.values() if not m.editable]

# The order of this list MUST match the order of display components, as defined in DatasetTab.py
DISPLAYED_DATASET_METADATA: list[FieldTypes] = (
    EDITABLE_DATASET_METADATA_LEFT
    + EDITABLE_DATASET_METADATA_RIGHT
    + NON_EDITABLE_DATASET_METADATA
)

DROPDOWN_DATASET_METADATA: list[MetadataDropdownField] = [
    m for m in DISPLAYED_DATASET_METADATA if isinstance(m, MetadataDropdownField)
]

DROPDOWN_DATASET_METADATA_IDENTIFIERS: list[str] = [
    m.identifier for m in DROPDOWN_DATASET_METADATA
]

OBLIGATORY_DATASET_METADATA_IDENTIFIERS_AND_DISPLAY_NAME: list[tuple] = [
    (m.identifier, m.display_name)
    for m in DISPLAY_DATASET.values()
    if m.obligatory and m.editable
]
