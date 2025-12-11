"""Functionality for displaying variables metadata."""

from __future__ import annotations

import functools
from enum import Enum
from typing import TYPE_CHECKING

from dapla_metadata.datasets import enums
from dapla_metadata.datasets.utility.urn import klass_urn_converter
from dapla_metadata.datasets.utility.urn import vardef_urn_converter

from datadoc_editor import state
from datadoc_editor.enums import DataType
from datadoc_editor.enums import TemporalityTypeType
from datadoc_editor.enums import VariableRole
from datadoc_editor.frontend.constants import DELETE_SELECTED
from datadoc_editor.frontend.constants import DESELECT
from datadoc_editor.frontend.constants import DROPDOWN_DELETE_OPTION
from datadoc_editor.frontend.constants import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_base import VARIABLES_METADATA_DATE_INPUT
from datadoc_editor.frontend.fields.display_base import (
    VARIABLES_METADATA_MULTILANGUAGE_INPUT,
)
from datadoc_editor.frontend.fields.display_base import FieldTypes
from datadoc_editor.frontend.fields.display_base import MetadataCheckboxField
from datadoc_editor.frontend.fields.display_base import MetadataDropdownField
from datadoc_editor.frontend.fields.display_base import MetadataInputField
from datadoc_editor.frontend.fields.display_base import MetadataMultiLanguageField
from datadoc_editor.frontend.fields.display_base import MetadataPeriodField
from datadoc_editor.frontend.fields.display_base import MetadataUrnField
from datadoc_editor.frontend.fields.display_base import get_data_source_options
from datadoc_editor.frontend.fields.display_base import (
    get_data_source_options_with_delete,
)
from datadoc_editor.frontend.fields.display_base import get_enum_options
from datadoc_editor.frontend.fields.display_base import (
    get_enum_options_with_delete_and_deselect_option,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def get_measurement_unit_options() -> list[dict[str, str]]:
    """Collect the measurement unit options."""
    dropdown_options = [
        {
            "title": measurement_unit.get_title(enums.SupportedLanguages.NORSK_BOKMÅL),
            "id": measurement_unit.code,
        }
        for measurement_unit in state.measurement_units.classifications
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DESELECT_OPTION, "id": ""})
    return dropdown_options


def get_measurement_unit_options_with_delete() -> list[dict[str, str]]:
    """Collect the measurement unit options with deselect and delete options."""
    dropdown_options = get_measurement_unit_options()
    dropdown_options[0] = {"title": DROPDOWN_DESELECT_OPTION, "id": DESELECT}
    dropdown_options.insert(1, {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED})

    return dropdown_options


def get_unit_type_options() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = [
        {
            "title": unit_type.get_title(enums.SupportedLanguages.NORSK_BOKMÅL),
            "id": unit_type.code,
        }
        for unit_type in state.unit_types.classifications
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DESELECT_OPTION, "id": ""})
    return dropdown_options


def get_unit_type_options_with_delete() -> list[dict[str, str]]:
    """Collect the unit type options with deselect and delete options."""
    dropdown_options = get_unit_type_options()
    dropdown_options[0] = {"title": DROPDOWN_DESELECT_OPTION, "id": DESELECT}
    dropdown_options.insert(1, {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED})

    return dropdown_options


class VariableIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst."""

    SHORT_NAME = "short_name"
    NAME = "name"
    DATA_TYPE = "data_type"
    VARIABLE_ROLE = "variable_role"
    DEFINITION_URI = "definition_uri"
    IS_PERSONAL_DATA = "is_personal_data"
    UNIT_TYPE = "unit_type"
    DATA_SOURCE = "data_source"
    POPULATION_DESCRIPTION = "population_description"
    COMMENT = "comment"
    TEMPORALITY_TYPE = "temporality_type"
    MEASUREMENT_UNIT = "measurement_unit"
    FORMAT = "format"
    CLASSIFICATION_URI = "classification_uri"
    INVALID_VALUE_DESCRIPTION = "invalid_value_description"
    IDENTIFIER = "id"
    CONTAINS_DATA_FROM = "contains_data_from"
    CONTAINS_DATA_UNTIL = "contains_data_until"
    DATA_ELEMENT_PATH = "data_element_path"
    MULTIPLICATION_FACTOR = "multiplication_factor"


DISPLAY_VARIABLES: dict[
    VariableIdentifiers,
    FieldTypes,
] = {
    VariableIdentifiers.NAME: MetadataMultiLanguageField(
        identifier=VariableIdentifiers.NAME.value,
        display_name="Navn",
        description="Variabelnavn som er forståelig for mennesker. Navnet kan arves fra lenket Vardef-variabel eller endres her (ev. oppgis her i tilfeller der variabelen ikke skal lenkes til Vardef).",
        obligatory=True,
        editable=True,
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
    ),
    VariableIdentifiers.DEFINITION_URI: MetadataUrnField(
        identifier=VariableIdentifiers.DEFINITION_URI.value,
        display_name="Variabeldefinisjon ID",
        description="Oppgi IDen til tilhørende variabeldefinisjon i Vardef.",
        obligatory=False,
        editable=True,
        converter=vardef_urn_converter,
    ),
    VariableIdentifiers.COMMENT: MetadataMultiLanguageField(
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Kommentaren har to funksjoner. Den skal brukes til å beskrive variabelforekomsten dersom denne ikke har lenke til Vardef (gjelder klargjorte data, statistikk og utdata), og den kan brukes til å gi ytterligere presiseringer av variabelforekomstens definisjon dersom variabelforekomsten er lenket til Vardef",
        obligatory=False,
        editable=True,
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
    ),
    VariableIdentifiers.IS_PERSONAL_DATA: MetadataCheckboxField(
        identifier=VariableIdentifiers.IS_PERSONAL_DATA.value,
        display_name="Er personopplysning",
        description="Dersom variabelen er en personopplysning, skal denne sjekkboksen være avkrysset. Dersom den ikke er en personopplysning, lar en bare defaultsvaret bli stående. All informasjon som entydig kan knyttes til en fysisk person (f.eks. fødselsnummer eller adresse) er personopplysninger. Næringsdata om enkeltpersonforetak (ENK) skal imidlertid ikke regnes som personopplysninger.",
        obligatory=True,
        editable=True,
    ),
    VariableIdentifiers.UNIT_TYPE: MetadataDropdownField(
        identifier=VariableIdentifiers.UNIT_TYPE.value,
        display_name="Enhetstype",
        description="Den enhetstypen variabelen inneholder informasjon om. Eksempler på enhetstyper er person, foretak og eiendom.",
        options_getter=get_unit_type_options,
        obligatory=True,
        editable=True,
        searchable=True,
    ),
    VariableIdentifiers.POPULATION_DESCRIPTION: MetadataMultiLanguageField(
        identifier=VariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen settes på datasettnivå, men kan spesifiseres eller overskrives (hvis variabelen har en annen populasjon enn de fleste andre variablene i datasettet) her.",
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
        obligatory=True,
        editable=True,
    ),
    VariableIdentifiers.MEASUREMENT_UNIT: MetadataDropdownField(
        identifier=VariableIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Dersom variabelen er kvantitativ, skal den ha en måleenhet, f.eks. kilo eller kroner.",
        options_getter=get_measurement_unit_options,
        obligatory=False,
        editable=True,
        searchable=True,
    ),
    VariableIdentifiers.INVALID_VALUE_DESCRIPTION: MetadataMultiLanguageField(
        identifier=VariableIdentifiers.INVALID_VALUE_DESCRIPTION.value,
        display_name="Ugyldige verdier",
        description="Feltet brukes til å beskrive ugyldige verdier som inngår i variabelen - dersom spesialverdiene ikke er tilstrekkelige eller ikke kan benyttes.",
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
        obligatory=False,
        editable=True,
    ),
    VariableIdentifiers.MULTIPLICATION_FACTOR: MetadataInputField(
        identifier=VariableIdentifiers.MULTIPLICATION_FACTOR.value,
        display_name="Multiplikasjonsfaktor",
        description="Multiplikasjonsfaktoren er den numeriske verdien som multipliseres med måleenheten, f.eks. når en skal vise store tall i en tabell, eksempelvis 1000 kroner.",
        type="number",
        obligatory=False,
        editable=True,
    ),
    VariableIdentifiers.VARIABLE_ROLE: MetadataDropdownField(
        identifier=VariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Oppgi hvilken rolle variabelen har i datasettet. De ulike rollene er identifikator ( identifiserer de ulike enhetene, f.eks. fødselsnummer og organisasjonsnummer), målevariabel ( beskriver egenskaper, f.eks. sivilstand og omsetning), startdato (beskriver startdato for variabler som har et forløp, eller måletidspunkt for tverrsnittdata), stoppdato(beskriver stoppdato for variabler som har et forløp) og attributt (brukes i tifeller der SSB utvider datasettet med egen informasjon, f.eks. datakvalitet eller editering)",
        obligatory=True,
        editable=True,
        options_getter=functools.partial(
            get_enum_options,
            VariableRole,
        ),
    ),
    VariableIdentifiers.CLASSIFICATION_URI: MetadataUrnField(
        identifier=VariableIdentifiers.CLASSIFICATION_URI.value,
        display_name="Kodeverk ID",
        description="ID til en klassifikasjon eller kodeliste i Klass. Variabelforekomster skal generelt knyttes til tilhørende kodeverk via relevant variabeldefinisjon i Vardef. Unntaksvis kan den imidlertid knyttes direkte til Klass via dette feltet (i tilfeller der det ikke er hensiktsmessig å definere variabelen i Vardef).",
        obligatory=False,
        editable=True,
        converter=klass_urn_converter,
    ),
    VariableIdentifiers.DATA_SOURCE: MetadataDropdownField(
        identifier=VariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilden til variabelen (på etat-/organisasjonsnivå).",
        options_getter=get_data_source_options,
        obligatory=True,
        editable=True,
        searchable=True,
    ),
    VariableIdentifiers.TEMPORALITY_TYPE: MetadataDropdownField(
        identifier=VariableIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitet sier noe om tidsdimensjonen for variabelen. Fast er data med verdi som ikke endres over tid (f.eks. fødselsdato), tverrsnitt er data som er målt på et gitt tidspunkt, akkumulert er data som  er samlet over en viss tidsperiode (f.eks. inntekt gjennom et år) og  hendelse/forløp registrerer tidspunkt og tidsperiode for ulike hendelser /tilstander, f.eks. (skifte av) bosted.",
        options_getter=functools.partial(
            get_enum_options,
            TemporalityTypeType,
        ),
        obligatory=True,
        editable=True,
    ),
    VariableIdentifiers.FORMAT: MetadataInputField(
        identifier=VariableIdentifiers.FORMAT.value,
        display_name="Format",
        description="Verdienes format (fysisk format eller regulært uttrykk) i maskinlesbar form ifm validering, f.eks.  ISO 8601 som datoformat. Dette feltet kan benyttes som en ytterligere presisering av datatype i tilfellene der det er relevant.",
        obligatory=False,
        editable=True,
    ),
    VariableIdentifiers.CONTAINS_DATA_FROM: MetadataPeriodField(
        identifier=VariableIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Variabelen inneholder data fra og med denne datoen.",
        id_type=VARIABLES_METADATA_DATE_INPUT,
        obligatory=False,
        editable=True,
    ),
    VariableIdentifiers.CONTAINS_DATA_UNTIL: MetadataPeriodField(
        identifier=VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="Variabelen inneholder data til og med denne datoen.",
        id_type=VARIABLES_METADATA_DATE_INPUT,
        obligatory=False,
        editable=True,
    ),
    VariableIdentifiers.SHORT_NAME: MetadataInputField(
        identifier=VariableIdentifiers.SHORT_NAME.value,
        display_name="Kortnavn",
        description="Fysisk navn på variabelen i datasettet. Bør tilsvare anbefalt kortnavn.",
        obligatory=True,
        editable=False,
    ),
    VariableIdentifiers.DATA_TYPE: MetadataDropdownField(
        identifier=VariableIdentifiers.DATA_TYPE.value,
        display_name="Datatype",
        description="Velg en av følgende datatyper: tekst, heltall, desimaltall, datotid eller boolsk. Dersom variabelen er knyttet til et kodeverk i Klass, velges datatype tekst.",
        obligatory=True,
        editable=True,
        options_getter=functools.partial(
            get_enum_options,
            DataType,
        ),
    ),
    VariableIdentifiers.DATA_ELEMENT_PATH: MetadataInputField(
        identifier=VariableIdentifiers.DATA_ELEMENT_PATH.value,
        display_name="Dataelementsti",
        description="For hierarkiske datasett (JSON) må sti til dataelementet oppgis i tillegg til kortnavn (shortName)",
        obligatory=False,
        editable=True,
    ),
    VariableIdentifiers.IDENTIFIER: MetadataInputField(
        identifier=VariableIdentifiers.IDENTIFIER.value,
        display_name="ID",
        description="Unik SSB identifikator for variabelforekomsten i datasettet",
        obligatory=False,
        editable=False,
    ),
}

MULTIPLE_LANGUAGE_VARIABLES_METADATA = [
    m.identifier
    for m in DISPLAY_VARIABLES.values()
    if isinstance(m, MetadataMultiLanguageField)
]

VARIABLES_METADATA_LEFT = [
    m
    for m in DISPLAY_VARIABLES.values()
    if (isinstance(m, MetadataMultiLanguageField) and m.editable)
]

VARIABLES_METADATA_RIGHT = [
    m
    for m in DISPLAY_VARIABLES.values()
    if not isinstance(m, MetadataMultiLanguageField) and m.editable
]

OBLIGATORY_VARIABLES_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if m.obligatory and m.editable
]

OPTIONAL_VARIABLES_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if not m.obligatory and m.editable
]

OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_AND_DISPLAY_NAME: list[tuple] = [
    (m.identifier, m.display_name)
    for m in DISPLAY_VARIABLES.values()
    if m.obligatory and m.editable
]

NON_EDITABLE_VARIABLES_METADATA = [
    m for m in DISPLAY_VARIABLES.values() if not m.editable
]

DISPLAY_GLOBALS: dict[
    VariableIdentifiers,
    FieldTypes,
] = {
    VariableIdentifiers.UNIT_TYPE: DISPLAY_VARIABLES[VariableIdentifiers.UNIT_TYPE],
    VariableIdentifiers.MEASUREMENT_UNIT: DISPLAY_VARIABLES[
        VariableIdentifiers.MEASUREMENT_UNIT
    ],
    VariableIdentifiers.MULTIPLICATION_FACTOR: DISPLAY_VARIABLES[
        VariableIdentifiers.MULTIPLICATION_FACTOR
    ],
    VariableIdentifiers.VARIABLE_ROLE: DISPLAY_VARIABLES[
        VariableIdentifiers.VARIABLE_ROLE
    ],
    VariableIdentifiers.DATA_SOURCE: DISPLAY_VARIABLES[VariableIdentifiers.DATA_SOURCE],
    VariableIdentifiers.TEMPORALITY_TYPE: DISPLAY_VARIABLES[
        VariableIdentifiers.TEMPORALITY_TYPE
    ],
}

GLOBAL_VARIABLES = list(DISPLAY_GLOBALS.values())

GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME: list[tuple] = [
    (m.identifier, m.display_name) for m in DISPLAY_GLOBALS.values()
]

GLOBAL_OPTIONS_GETTERS: dict[str, Callable[[], list[dict[str, str]]]] = {
    DISPLAY_GLOBALS[
        VariableIdentifiers.DATA_SOURCE
    ].identifier: get_data_source_options_with_delete,
    DISPLAY_GLOBALS[
        VariableIdentifiers.MEASUREMENT_UNIT
    ].identifier: get_measurement_unit_options_with_delete,
    DISPLAY_GLOBALS[
        VariableIdentifiers.UNIT_TYPE
    ].identifier: get_unit_type_options_with_delete,
    DISPLAY_GLOBALS[VariableIdentifiers.TEMPORALITY_TYPE].identifier: functools.partial(
        get_enum_options_with_delete_and_deselect_option, TemporalityTypeType
    ),
    DISPLAY_GLOBALS[VariableIdentifiers.VARIABLE_ROLE].identifier: functools.partial(
        get_enum_options_with_delete_and_deselect_option, VariableRole
    ),
}
