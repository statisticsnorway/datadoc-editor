import functools
from enum import Enum

from datadoc_editor.enums import TemporalityTypeType
from datadoc_editor.enums import VariableRole
from datadoc_editor.frontend.fields.display_base import GlobalDropdownField
from datadoc_editor.frontend.fields.display_base import GlobalFieldTypes
from datadoc_editor.frontend.fields.display_base import GlobalInputField
from datadoc_editor.frontend.fields.display_base import get_data_source_options
from datadoc_editor.frontend.fields.display_base import get_enum_options
from datadoc_editor.frontend.fields.display_variables import (
    get_measurement_unit_options,
)
from datadoc_editor.frontend.fields.display_variables import get_unit_type_options

GLOBAL_VARIABLES_INPUT = "global-variables-input"
GLOBAL_HEADER = "Globale verdier"

GLOBAL_HEADER_INFORMATION = "Hva, hvorfor og hvordan."


class GlobalIdentifiers(str, Enum):
    """Fields which can be globally edited."""

    DATA_TYPE = "data_type"
    VARIABLE_ROLE = "variable_role"
    UNIT_TYPE = "unit_type"
    DATA_SOURCE = "data_source"
    TEMPORALITY_TYPE = "temporality_type"
    MEASUREMENT_UNIT = "measurement_unit"
    MULTIPLICATION_FACTOR = "multiplication_factor"


DISPLAY_GLOBALS: dict[
    GlobalIdentifiers,
    GlobalFieldTypes,
] = {
    GlobalIdentifiers.UNIT_TYPE: GlobalDropdownField(
        identifier=GlobalIdentifiers.UNIT_TYPE.value,
        display_name="Enhetstype",
        description="Den enhetstypen variabelen inneholder informasjon om. Eksempler på enhetstyper er person, foretak og eiendom.",
        obligatory=True,
        options_getter=get_unit_type_options,
    ),
    GlobalIdentifiers.MEASUREMENT_UNIT: GlobalDropdownField(
        identifier=GlobalIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Dersom variabelen er kvantitativ, skal den ha en måleenhet, f.eks. kilo eller kroner.",
        options_getter=get_measurement_unit_options,
    ),
    GlobalIdentifiers.MULTIPLICATION_FACTOR: GlobalInputField(
        identifier=GlobalIdentifiers.MULTIPLICATION_FACTOR.value,
        display_name="Multiplikasjonsfaktor",
        description="Multiplikasjonsfaktoren er den numeriske verdien som multipliseres med måleenheten, f.eks. når en skal vise store tall i en tabell, eksempelvis 1000 kroner.",
        type="number",
    ),
    GlobalIdentifiers.VARIABLE_ROLE: GlobalDropdownField(
        identifier=GlobalIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Oppgi hvilken rolle variabelen har i datasettet. De ulike rollene er identifikator ( identifiserer de ulike enhetene, f.eks. fødselsnummer og organisasjonsnummer), målevariabel ( beskriver egenskaper, f.eks. sivilstand og omsetning), startdato (beskriver startdato for variabler som har et forløp, eller måletidspunkt for tverrsnittdata), stoppdato(beskriver stoppdato for variabler som har et forløp) og attributt (brukes i tifeller der SSB utvider datasettet med egen informasjon, f.eks. datakvalitet eller editering)",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options,
            VariableRole,
        ),
    ),
    GlobalIdentifiers.DATA_SOURCE: GlobalDropdownField(
        identifier=GlobalIdentifiers.DATA_SOURCE.value,
        display_name="Datakilde",
        description="Datakilden til variabelen (på etat-/organisasjonsnivå).",
        obligatory=True,
        options_getter=get_data_source_options,
    ),
    GlobalIdentifiers.TEMPORALITY_TYPE: GlobalDropdownField(
        identifier=GlobalIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitet sier noe om tidsdimensjonen for variabelen. Fast er data med verdi som ikke endres over tid (f.eks. fødselsdato), tverrsnitt er data som er målt på et gitt tidspunkt, akkumulert er data som  er samlet over en viss tidsperiode (f.eks. inntekt gjennom et år) og  hendelse/forløp registrerer tidspunkt og tidsperiode for ulike hendelser /tilstander, f.eks. (skifte av) bosted.",
        obligatory=True,
        options_getter=functools.partial(
            get_enum_options,
            TemporalityTypeType,
        ),
    ),
}

GLOBAL_VARIABLES = list(DISPLAY_GLOBALS.values())

GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME: list[tuple] = [
    (m.identifier, m.display_name) for m in DISPLAY_GLOBALS.values()
]
