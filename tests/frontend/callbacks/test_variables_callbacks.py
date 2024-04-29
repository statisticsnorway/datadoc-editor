"""Tests for the variables callbacks module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

import arrow
import pytest
from datadoc_model.model import LanguageStringTypeItem
from pydantic_core import Url

from datadoc import enums
from datadoc import state
from datadoc.frontend.callbacks.variables import accept_variable_metadata_date_input
from datadoc.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc.frontend.callbacks.variables import populate_variables_workspace
from datadoc.frontend.callbacks.variables import set_variables_value_multilanguage
from datadoc.frontend.callbacks.variables import (
    set_variables_values_inherited_from_dataset,
)
from datadoc.frontend.fields.display_base import get_metadata_and_stringify
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc.frontend.fields.display_variables import VariableIdentifiers
from datadoc.frontend.text import INVALID_DATE_ORDER
from datadoc.frontend.text import INVALID_VALUE

if TYPE_CHECKING:
    from datadoc.backend.datadoc_metadata import DataDocMetadata
    from datadoc.frontend.callbacks.utils import MetadataInputTypes


@pytest.mark.parametrize(
    ("metadata_field", "value", "expected_model_value"),
    [
        (
            VariableIdentifiers.NAME,
            "Variable name",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Variable name",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.DATA_TYPE,
            enums.DataType.STRING,
            enums.DataType.STRING.value,
        ),
        (
            VariableIdentifiers.VARIABLE_ROLE,
            enums.VariableRole.MEASURE,
            enums.VariableRole.MEASURE.value,
        ),
        (
            VariableIdentifiers.DEFINITION_URI,
            "https://www.example.com",
            Url("https://www.example.com"),
        ),
        (
            VariableIdentifiers.DIRECT_PERSON_IDENTIFYING,
            True,
            True,
        ),
        (
            VariableIdentifiers.DATA_SOURCE,
            "Atlantis",
            "Atlantis",
        ),
        (
            VariableIdentifiers.POPULATION_DESCRIPTION,
            "Population description",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Population description",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.COMMENT,
            "Comment",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Comment",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.TEMPORALITY_TYPE,
            enums.TemporalityTypeType.ACCUMULATED,
            enums.TemporalityTypeType.ACCUMULATED.value,
        ),
        (
            VariableIdentifiers.MEASUREMENT_UNIT,
            "Kilograms",
            "Kilograms",
        ),
        (
            VariableIdentifiers.FORMAT,
            "Regex",
            "Regex",
        ),
        (
            VariableIdentifiers.CLASSIFICATION_URI,
            "https://www.example.com",
            Url("https://www.example.com"),
        ),
        (
            VariableIdentifiers.INVALID_VALUE_DESCRIPTION,
            "Invalid value",
            enums.LanguageStringType(
                [
                    enums.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Invalid value",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.IDENTIFIER,
            "2f72477a-f051-43ee-bf8b-0d8f47b5e0a7",
            UUID("2f72477a-f051-43ee-bf8b-0d8f47b5e0a7"),
        ),
    ],
)
def test_accept_variable_metadata_input_valid(
    metadata: DataDocMetadata,
    metadata_field: VariableIdentifiers,
    value: MetadataInputTypes,
    expected_model_value: Any,  # noqa: ANN401
):
    state.metadata = metadata
    assert (
        accept_variable_metadata_input(
            value,
            metadata.variables[0].short_name,
            metadata_field=metadata_field.value,
            language="nb",
        )
        is None
    )
    assert (
        getattr(state.metadata.variables[0], metadata_field.value)
        == expected_model_value
    )


def test_accept_variable_metadata_input_invalid(
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    message = accept_variable_metadata_input(
        "not a url",
        metadata.variables[0].short_name,
        metadata_field=VariableIdentifiers.DEFINITION_URI.value,
    )
    assert message is not None
    assert message == INVALID_VALUE


@pytest.mark.parametrize(
    (
        "variable_identifier",
        "contains_data_from",
        "contains_data_until",
        "expected_result",
    ),
    [
        (
            VariableIdentifiers.CONTAINS_DATA_FROM.value,
            "1950-01-01",
            "2020-01-01",
            (False, "", False, ""),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_FROM.value,
            "2020-01-01",
            "1950-01-01",
            (
                True,
                INVALID_DATE_ORDER.format(
                    contains_data_from_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_FROM
                    ].display_name,
                    contains_data_until_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_UNTIL
                    ].display_name,
                ),
                False,
                "",
            ),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            "1950-01-01",
            "2020-01-01",
            (False, "", False, ""),
        ),
        (
            VariableIdentifiers.CONTAINS_DATA_UNTIL.value,
            "2020-01-01",
            "1950-01-01",
            (
                False,
                "",
                True,
                INVALID_DATE_ORDER.format(
                    contains_data_from_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_FROM
                    ].display_name,
                    contains_data_until_display_name=DISPLAY_VARIABLES[
                        VariableIdentifiers.CONTAINS_DATA_UNTIL
                    ].display_name,
                ),
            ),
        ),
    ],
)
def test_accept_variable_metadata_date_input(
    variable_identifier,
    contains_data_from: str,
    contains_data_until: str,
    expected_result: tuple[bool, str, bool, str],
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    chosen_short_name = metadata.variables[0].short_name
    preset_identifier = (
        VariableIdentifiers.CONTAINS_DATA_UNTIL.value
        if variable_identifier == VariableIdentifiers.CONTAINS_DATA_FROM.value
        else VariableIdentifiers.CONTAINS_DATA_FROM.value
    )
    preset_value = (
        contains_data_until
        if variable_identifier == VariableIdentifiers.CONTAINS_DATA_FROM.value
        else contains_data_from
    )
    setattr(
        state.metadata.variables_lookup[chosen_short_name],
        preset_identifier,
        arrow.get(preset_value).date(),
    )
    assert (
        accept_variable_metadata_date_input(
            VariableIdentifiers(variable_identifier),
            chosen_short_name,
            contains_data_from,
            contains_data_until,
        )
        == expected_result
    )
    if not expected_result[0]:
        assert (
            metadata.variables[0].contains_data_from
            == arrow.get(
                contains_data_from,
            ).date()
        )
    if not expected_result[2]:
        assert (
            metadata.variables[0].contains_data_until
            == arrow.get(
                contains_data_until,
            ).date()
        )


@pytest.mark.usefixtures("_code_list_fake_classifications_variables")
@pytest.mark.parametrize(
    ("search_query", "expected_length"),
    [
        (
            "",
            8,
        ),
        (
            "a",
            4,
        ),
        (
            "pers_id",
            1,
        ),
    ],
)
def test_populate_variables_workspace_filter_variables(
    search_query: str,
    expected_length: int,
    metadata: DataDocMetadata,
):
    assert (
        len(
            populate_variables_workspace(
                metadata.variables,
                search_query,
                0,
            ),
        )
        == expected_length
    )


@pytest.mark.parametrize(
    (
        "dataset_value",
        "dataset_identifier",
        "variable_identifier",
    ),
    [
        (
            "STATUS",
            DatasetIdentifiers.TEMPORALITY_TYPE,
            VariableIdentifiers.TEMPORALITY_TYPE,
        ),
        (
            "01",
            DatasetIdentifiers.DATA_SOURCE,
            VariableIdentifiers.DATA_SOURCE,
        ),
        (
            "2009-01-02",
            DatasetIdentifiers.CONTAINS_DATA_FROM,
            VariableIdentifiers.CONTAINS_DATA_FROM,
        ),
        (
            "2021-08-10",
            DatasetIdentifiers.CONTAINS_DATA_UNTIL,
            VariableIdentifiers.CONTAINS_DATA_UNTIL,
        ),
    ],
)
def test_variables_values_inherit_dataset_values(
    dataset_value,
    dataset_identifier,
    variable_identifier,
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    setattr(
        state.metadata.dataset,
        dataset_identifier,
        dataset_value,
    )
    set_variables_values_inherited_from_dataset(
        dataset_value,
        dataset_identifier,
    )
    for val in state.metadata.variables:
        assert dataset_value == get_metadata_and_stringify(
            metadata.variables_lookup[val.short_name],
            variable_identifier.value,
        )


@pytest.mark.parametrize(
    (
        "dataset_value",
        "dataset_identifier",
        "variable_identifier",
        "update_value",
    ),
    [
        (
            "EVENT",
            DatasetIdentifiers.TEMPORALITY_TYPE,
            VariableIdentifiers.TEMPORALITY_TYPE,
            "ACCUMULATED",
        ),
        (
            "02",
            DatasetIdentifiers.DATA_SOURCE,
            VariableIdentifiers.DATA_SOURCE,
            "03",
        ),
        (
            "2009-01-02",
            DatasetIdentifiers.CONTAINS_DATA_FROM,
            VariableIdentifiers.CONTAINS_DATA_FROM,
            "1998-03-11",
        ),
        (
            "1988-11-03",
            DatasetIdentifiers.CONTAINS_DATA_UNTIL,
            VariableIdentifiers.CONTAINS_DATA_UNTIL,
            "2008-01-01",
        ),
    ],
)
def test_variables_values_can_be_changed_after_update_from_dataset_value(
    dataset_value,
    dataset_identifier,
    variable_identifier,
    update_value,
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    setattr(
        state.metadata.dataset,
        dataset_identifier,
        dataset_value,
    )
    set_variables_values_inherited_from_dataset(
        dataset_value,
        dataset_identifier,
    )
    for val in state.metadata.variables:
        assert dataset_value == get_metadata_and_stringify(
            metadata.variables_lookup[val.short_name],
            variable_identifier,
        )
    setattr(
        state.metadata.variables_lookup["pers_id"],
        variable_identifier,
        update_value,
    )
    assert dataset_value == get_metadata_and_stringify(
        metadata.variables_lookup["sivilstand"],
        variable_identifier.value,
    )
    assert dataset_value != get_metadata_and_stringify(
        metadata.variables_lookup["pers_id"],
        variable_identifier.value,
    )
    assert (
        get_metadata_and_stringify(
            metadata.variables_lookup["pers_id"],
            variable_identifier.value,
        )
        == update_value
    )


def test_update_variables_multilanguage_values_from_dataset_values(
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    dataset_population_description = "Personer bosatt i Norge"
    dataset_population_description_language_item = [
        LanguageStringTypeItem(
            languageCode="nb",
            languageText="Personer bosatt i Norge",
        ),
    ]
    metadata_identifier = DatasetIdentifiers.POPULATION_DESCRIPTION
    language = "nb"
    setattr(
        state.metadata.dataset,
        metadata_identifier,
        dataset_population_description_language_item,
    )
    set_variables_value_multilanguage(
        dataset_population_description,
        metadata_identifier,
        language,
    )
    for val in state.metadata.variables:
        assert metadata.dataset.population_description == get_standard_metadata(
            metadata.variables_lookup[val.short_name],
            VariableIdentifiers.POPULATION_DESCRIPTION.value,
        )


def test_variables_multilanguage_value_can_be_changed_after_update_from_dataset_value(
    metadata: DataDocMetadata,
):
    state.metadata = metadata
    dataset_population_description = "Persons in Norway"
    dataset_population_description_language_item = [
        LanguageStringTypeItem(languageCode="en", languageText="Persons in Norway"),
    ]
    dataset_identifier = DatasetIdentifiers.POPULATION_DESCRIPTION
    variables_identifier = VariableIdentifiers.POPULATION_DESCRIPTION
    language = "en"
    setattr(
        state.metadata.dataset,
        dataset_identifier,
        dataset_population_description_language_item,
    )
    set_variables_value_multilanguage(
        dataset_population_description,
        dataset_identifier,
        language,
    )
    for val in state.metadata.variables:
        assert metadata.dataset.population_description == get_standard_metadata(
            metadata.variables_lookup[val.short_name],
            variables_identifier,
        )
    variables_language_item = [
        LanguageStringTypeItem(languageCode="en", languageText="Persons in Sweden"),
    ]
    setattr(
        state.metadata.variables_lookup["pers_id"],
        variables_identifier,
        variables_language_item,
    )
    assert metadata.dataset.population_description != get_standard_metadata(
        metadata.variables_lookup["pers_id"],
        variables_identifier,
    )
    assert metadata.dataset.population_description == get_standard_metadata(
        metadata.variables_lookup["sivilstand"],
        variables_identifier,
    )
