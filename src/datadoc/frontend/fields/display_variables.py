"""Functionality for displaying variables metadata."""

from __future__ import annotations

import functools
from enum import Enum

from dapla_metadata.datasets import enums

from datadoc import state
from datadoc.enums import DataType
from datadoc.enums import IsPersonalData
from datadoc.enums import TemporalityTypeType
from datadoc.enums import VariableRole
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_DATE_INPUT
from datadoc.frontend.fields.display_base import VARIABLES_METADATA_MULTILANGUAGE_INPUT
from datadoc.frontend.fields.display_base import FieldTypes
from datadoc.frontend.fields.display_base import MetadataDropdownField
from datadoc.frontend.fields.display_base import MetadataInputField
from datadoc.frontend.fields.display_base import MetadataMultiLanguageField
from datadoc.frontend.fields.display_base import MetadataPeriodField
from datadoc.frontend.fields.display_base import get_data_source_options
from datadoc.frontend.fields.display_base import get_enum_options


def get_measurement_unit_options() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = [
        {
            "title": measurement_unit.get_title(enums.SupportedLanguages.NORSK_BOKMÅL),
            "id": measurement_unit.code,
        }
        for measurement_unit in state.measurement_units.classifications
    ]
    dropdown_options.insert(0, {"title": "", "id": ""})
    return dropdown_options


class VariableIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst."""

    SHORT_NAME = "short_name"
    NAME = "name"
    DATA_TYPE = "data_type"
    VARIABLE_ROLE = "variable_role"
    DEFINITION_URI = "definition_uri"
    IS_PERSONAL_DATA = "is_personal_data"
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
        description="Variabelnavn som er forståelig for mennesker. Navnet kan arves fra  lenket VarDef-variabel eller endres her (ev. oppgis her i tilfeller der variabelen ikke skal lenkes til VarDef).",
        obligatory=True,
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
    ),
    VariableIdentifiers.DEFINITION_URI: MetadataInputField(
        identifier=VariableIdentifiers.DEFINITION_URI.value,
        display_name="Definition URI",
        description="Oppgi lenke (URI) til tilhørende variabel i VarDef.",
        obligatory=False,
    ),
    VariableIdentifiers.COMMENT: MetadataMultiLanguageField(
        identifier=VariableIdentifiers.COMMENT.value,
        display_name="Kommentar",
        description="Kommentaren har to funksjoner. Den skal brukes til å beskrive variabelforekomsten dersom denne ikke har lenke til VarDef (gjelder klargjorte data, statistikk og utdata), og den kan brukes til å gi ytterligere presiseringer av variabelforekomstens definisjon dersom variabelforekomsten er lenket til VarDef",
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
    ),
    VariableIdentifiers.IS_PERSONAL_DATA: MetadataDropdownField(
        identifier=VariableIdentifiers.IS_PERSONAL_DATA.value,
        display_name="Er personopplysning",
        description="Dersom variabelen er en personopplysning, skal det oppgis om den er pseudonymisert/kryptert eller ikke. Dersom den ikke er en personopplysning, lar en bare defaultsvaret «Ikke personopplysning» bli stående. All informasjon som entydig kan knyttes til en fysisk person (f.eks. fødselsnummer eller adresse) er personopplysninger. Næringsdata om enkeltpersonforetak (ENK) skal imidlertid ikke regnes som personopplysninger.",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options,
            IsPersonalData,
        ),
    ),
    VariableIdentifiers.POPULATION_DESCRIPTION: MetadataMultiLanguageField(
        identifier=VariableIdentifiers.POPULATION_DESCRIPTION.value,
        display_name="Populasjonen",
        description="Populasjonen settes på datasettnivå, men kan spesifiseres eller overskrives (hvis variabelen har en annen populasjon enn de fleste andre variablene i datasettet) her.",
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
    ),
    VariableIdentifiers.MEASUREMENT_UNIT: MetadataDropdownField(
        identifier=VariableIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Dersom variabelen er kvantitativ, skal den ha en måleenhet, f.eks. kilo eller kroner.",
        options_getter=get_measurement_unit_options,
    ),
    VariableIdentifiers.INVALID_VALUE_DESCRIPTION: MetadataMultiLanguageField(
        identifier=VariableIdentifiers.INVALID_VALUE_DESCRIPTION.value,
        display_name="Ugyldige verdier",
        description="Feltet brukes til å beskrive ugyldige verdier som inngår i variabelen - dersom spesialverdiene ikke er tilstrekkelige eller ikke kan benyttes.",
        id_type=VARIABLES_METADATA_MULTILANGUAGE_INPUT,
    ),
    VariableIdentifiers.MULTIPLICATION_FACTOR: MetadataInputField(
        identifier=VariableIdentifiers.MULTIPLICATION_FACTOR.value,
        display_name="Multiplikasjonsfaktor",
        description="Multiplikasjonsfaktoren er den numeriske verdien som multipliseres med måleenheten, f.eks. når en skal vise store tall i en tabell, eksempelvis 1000 kroner.",
        type="number",
    ),
    VariableIdentifiers.VARIABLE_ROLE: MetadataDropdownField(
        identifier=VariableIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Oppgi hvilken rolle variabelen har i datasettet. De ulike rollene er identifikator ( identifiserer de ulike enhetene, f.eks. fødselsnummer og organisasjonsnummer), målevariabel ( beskriver egenskaper, f.eks. sivilstand og omsetning), startdato (beskriver startdato for variabler som har et forløp, eller måletidspunkt for tverrsnittdata), stoppdato(beskriver stoppdato for variabler som har et forløp) og attributt (brukes i tifeller der SSB utvider datasettet med egen informasjon, f.eks. datakvalitet eller editering)",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options,
            VariableRole,
        ),
    ),
    VariableIdentifiers.CLASSIFICATION_URI: MetadataInputField(
        identifier=VariableIdentifiers.CLASSIFICATION_URI.value,
        display_name="Kodeverkets URI",
        description="Lenke (URI) til gyldige kodeverk (klassifikasjon eller kodeliste) i KLASS eller Klass-uttrekk. Variabelforekomster skal generelt knyttes til tilhørende kodeverk via relevant variabeldefinisjon i Vardef. Unntaksvis kan den imidlertid knyttes direkte til Klass via dette feltet (i tilfeller der det ikke er hensiktsmessig å definere variabelen i Vardef).",
    ),
    VariableIdentifiers.DATA_SOURCE: MetadataDropdownField(
        identifier=VariableIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Oppgi datakilden til variabelen (på etat-/organisasjonsnivå) dersom denne ikke allerede er satt på  datasettnivå. Brukes hovedsakelig når variabler i et datasett har ulike datakilder.",
        options_getter=get_data_source_options,
    ),
    VariableIdentifiers.TEMPORALITY_TYPE: MetadataDropdownField(
        identifier=VariableIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitetstypen settes vanligvis på datasettnivå, men dersom datasettet består av variabler med ulike temporalitetstyper, kan den settes på variabelnivå. Temporalitet sier noe om tidsdimensjonen i datasettet. Fast er data med verdi som ikke endres over tid (f.eks. fødselsdato), tverrsnitt er data som er målt på et gitt tidspunkt, akkumulert er data som  er samlet over en viss tidsperiode (f.eks. inntekt gjennom et år) og  hendelse/forløp registrerer tidspunkt og tidsperiode for ulike hendelser /tilstander, f.eks. (skifte av) bosted.",
        options_getter=functools.partial(
            get_enum_options,
            TemporalityTypeType,
        ),
    ),
    VariableIdentifiers.FORMAT: MetadataInputField(
        identifier=VariableIdentifiers.FORMAT.value,
        display_name="Format",
        description="Verdienes format (fysisk format eller regulært uttrykk) i maskinlesbar form ifm validering, f.eks.  ISO 8601 som datoformat. Dette feltet kan benyttes som en ytterligere presisering av datatype i tilfellene der det er relevant.",
    ),
    VariableIdentifiers.CONTAINS_DATA_FROM: MetadataPeriodField(
        identifier=VariableIdentifiers.CONTAINS_DATA_FROM.value,
        display_name="Inneholder data f.o.m.",
        description="Variabelen inneholder data fra og med denne datoen.",
        id_type=VARIABLES_METADATA_DATE_INPUT,
    ),
    VariableIdentifiers.CONTAINS_DATA_UNTIL: MetadataPeriodField(
        identifier=VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
        display_name="Inneholder data t.o.m.",
        description="Variabelen inneholder data til og med denne datoen.",
        id_type=VARIABLES_METADATA_DATE_INPUT,
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
        options_getter=functools.partial(
            get_enum_options,
            DataType,
        ),
    ),
    VariableIdentifiers.DATA_ELEMENT_PATH: MetadataInputField(
        identifier=VariableIdentifiers.DATA_ELEMENT_PATH.value,
        display_name="Dataelementsti",
        description="For hierarkiske datasett (JSON) må sti til dataelementet oppgis i tillegg til kortnavn (shortName)",
    ),
    VariableIdentifiers.IDENTIFIER: MetadataInputField(
        identifier=VariableIdentifiers.IDENTIFIER.value,
        display_name="ID",
        description="Unik SSB identifikator for variabelforekomsten i datasettet",
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
