from __future__ import annotations

import functools
from enum import Enum

from dapla_metadata.datasets import enums

from datadoc_editor import state
from datadoc_editor.constants import DELETE_SELECTED
from datadoc_editor.constants import DROPDOWN_DELETE_OPTION
from datadoc_editor.enums import TemporalityTypeType
from datadoc_editor.enums import VariableRole
from datadoc_editor.frontend.fields.display_base import GlobalDropdownField
from datadoc_editor.frontend.fields.display_base import GlobalFieldTypes
from datadoc_editor.frontend.fields.display_base import GlobalInputField
from datadoc_editor.frontend.fields.display_base import get_data_source_options
from datadoc_editor.frontend.fields.display_base import get_enum_options
from datadoc_editor.frontend.fields.display_variables import get_unit_type_options

GLOBAL_METADATA_INPUT = "global-variables-input"


def get_measurement_unit_options_with_delete() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = [
        {
            "title": measurement_unit.get_title(enums.SupportedLanguages.NORSK_BOKMÅL),
            "id": measurement_unit.code,
        }
        for measurement_unit in state.measurement_units.classifications
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DELETE_OPTION, "id": ""})
    return dropdown_options


def get_unit_type_options_with_delete() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = [
        {
            "title": unit_type.get_title(enums.SupportedLanguages.NORSK_BOKMÅL),
            "id": unit_type.code,
        }
        for unit_type in state.unit_types.classifications
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED})
    return dropdown_options


def get_data_source_options_with_delete() -> list[dict[str, str]]:
    """Collect the unit type options."""
    dropdown_options = [
        {
            "title": data_sources.get_title(enums.SupportedLanguages.NORSK_BOKMÅL),
            "id": data_sources.code,
        }
        for data_sources in state.data_sources.classifications
    ]
    dropdown_options.insert(0, {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED})
    return dropdown_options


class GlobalIdentifiers(str, Enum):
    """As defined here: https://statistics-norway.atlassian.net/wiki/spaces/MPD/pages/3042869256/Variabelforekomst."""

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
        global_editable=True,
        options_getter=get_unit_type_options,
    ),
    GlobalIdentifiers.MEASUREMENT_UNIT: GlobalDropdownField(
        identifier=GlobalIdentifiers.MEASUREMENT_UNIT.value,
        display_name="Måleenhet",
        description="Dersom variabelen er kvantitativ, skal den ha en måleenhet, f.eks. kilo eller kroner.",
        global_editable=True,
        options_getter=get_measurement_unit_options_with_delete,
    ),
    GlobalIdentifiers.MULTIPLICATION_FACTOR: GlobalInputField(
        identifier=GlobalIdentifiers.MULTIPLICATION_FACTOR.value,
        display_name="Multiplikasjonsfaktor",
        description="Multiplikasjonsfaktoren er den numeriske verdien som multipliseres med måleenheten, f.eks. når en skal vise store tall i en tabell, eksempelvis 1000 kroner.",
        type="number",
        global_editable=True,
    ),
    GlobalIdentifiers.VARIABLE_ROLE: GlobalDropdownField(
        identifier=GlobalIdentifiers.VARIABLE_ROLE.value,
        display_name="Variabelens rolle",
        description="Oppgi hvilken rolle variabelen har i datasettet. De ulike rollene er identifikator ( identifiserer de ulike enhetene, f.eks. fødselsnummer og organisasjonsnummer), målevariabel ( beskriver egenskaper, f.eks. sivilstand og omsetning), startdato (beskriver startdato for variabler som har et forløp, eller måletidspunkt for tverrsnittdata), stoppdato(beskriver stoppdato for variabler som har et forløp) og attributt (brukes i tifeller der SSB utvider datasettet med egen informasjon, f.eks. datakvalitet eller editering)",
        obligatory=True,
        global_editable=True,
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
        global_editable=True,
        options_getter=get_data_source_options,
    ),
    GlobalIdentifiers.TEMPORALITY_TYPE: GlobalDropdownField(
        identifier=GlobalIdentifiers.TEMPORALITY_TYPE.value,
        display_name="Temporalitetstype",
        description="Temporalitet sier noe om tidsdimensjonen for variabelen. Fast er data med verdi som ikke endres over tid (f.eks. fødselsdato), tverrsnitt er data som er målt på et gitt tidspunkt, akkumulert er data som  er samlet over en viss tidsperiode (f.eks. inntekt gjennom et år) og  hendelse/forløp registrerer tidspunkt og tidsperiode for ulike hendelser /tilstander, f.eks. (skifte av) bosted.",
        obligatory=True,
        global_editable=True,
        options_getter=functools.partial(
            get_enum_options,
            TemporalityTypeType,
        ),
    ),
}


GLOBAL_VARIABLES = list(DISPLAY_GLOBALS.values())
