"""Tests for the variables callbacks module."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

import arrow
import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import ObligatoryVariableWarning
from dapla_metadata.datasets import model
from pydantic import AnyUrl

from datadoc_editor import enums
from datadoc_editor import state
from datadoc_editor.frontend.callbacks.utils import variables_control
from datadoc_editor.frontend.callbacks.variables import (
    accept_pseudo_variable_metadata_input,
)
from datadoc_editor.frontend.callbacks.variables import (
    accept_variable_metadata_date_input,
)
from datadoc_editor.frontend.callbacks.variables import accept_variable_metadata_input
from datadoc_editor.frontend.callbacks.variables import populate_variables_workspace
from datadoc_editor.frontend.callbacks.variables import (
    set_variables_value_multilanguage_inherit_dataset_values,
)
from datadoc_editor.frontend.callbacks.variables import (
    set_variables_values_inherit_dataset_derived_date_values,
)
from datadoc_editor.frontend.callbacks.variables import (
    set_variables_values_inherit_dataset_values,
)
from datadoc_editor.frontend.constants import INVALID_DATE_ORDER
from datadoc_editor.frontend.constants import INVALID_VALUE
from datadoc_editor.frontend.fields.display_base import get_metadata_and_stringify
from datadoc_editor.frontend.fields.display_base import get_standard_metadata
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PseudoVariableIdentifiers,
)
from datadoc_editor.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers

if TYPE_CHECKING:
    from dapla_metadata.datasets import Datadoc

    from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes


@pytest.fixture
def n_clicks_1():
    return 1


@pytest.mark.parametrize(
    ("metadata_field", "value", "expected_model_value"),
    [
        (
            VariableIdentifiers.NAME,
            "Variable name",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
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
            AnyUrl("https://www.example.com"),
        ),
        (
            VariableIdentifiers.IS_PERSONAL_DATA,
            enums.IsPersonalData.NOT_PERSONAL_DATA,
            enums.IsPersonalData.NOT_PERSONAL_DATA.value,
        ),
        (
            VariableIdentifiers.DATA_SOURCE,
            "Atlantis",
            "Atlantis",
        ),
        (
            VariableIdentifiers.POPULATION_DESCRIPTION,
            "Population description",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Population description",
                    ),
                ],
            ),
        ),
        (
            VariableIdentifiers.COMMENT,
            "Comment",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
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
            AnyUrl("https://www.example.com"),
        ),
        (
            VariableIdentifiers.INVALID_VALUE_DESCRIPTION,
            "Invalid value",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
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
    metadata: Datadoc,
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
    metadata: Datadoc,
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
    metadata: Datadoc,
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


@pytest.mark.usefixtures("_code_list_fake_classifications")
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
    search_query: str, expected_length: int, metadata: Datadoc
):
    assert (
        len(
            populate_variables_workspace(metadata.variables, search_query, 0),
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
    metadata: Datadoc,
):
    state.metadata = metadata
    setattr(
        state.metadata.dataset,
        dataset_identifier,
        dataset_value,
    )
    set_variables_values_inherit_dataset_values(
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
def test_variables_values_can_be_changed_after_inherit_dataset_value(
    dataset_value,
    dataset_identifier,
    variable_identifier,
    update_value,
    metadata: Datadoc,
):
    state.metadata = metadata
    setattr(
        state.metadata.dataset,
        dataset_identifier,
        dataset_value,
    )
    set_variables_values_inherit_dataset_values(
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


def test_variables_values_multilanguage_inherit_dataset_values(
    metadata: Datadoc,
):
    state.metadata = metadata
    dataset_population_description = "Personer bosatt i Norge"
    dataset_population_description_language_item = [
        model.LanguageStringTypeItem(
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
    set_variables_value_multilanguage_inherit_dataset_values(
        dataset_population_description,
        metadata_identifier,
        language,
    )
    for val in state.metadata.variables:
        assert metadata.dataset.population_description == get_standard_metadata(
            metadata.variables_lookup[val.short_name],
            VariableIdentifiers.POPULATION_DESCRIPTION.value,
        )


def test_variables_values_multilanguage_can_be_changed_after_inherit_dataset_value(
    metadata: Datadoc,
):
    state.metadata = metadata
    dataset_population_description = "Persons in Norway"
    dataset_population_description_language_item = [
        model.LanguageStringTypeItem(
            languageCode="en",
            languageText="Persons in Norway",
        ),
    ]
    dataset_identifier = DatasetIdentifiers.POPULATION_DESCRIPTION
    variables_identifier = VariableIdentifiers.POPULATION_DESCRIPTION
    language = "en"
    setattr(
        state.metadata.dataset,
        dataset_identifier,
        dataset_population_description_language_item,
    )
    set_variables_value_multilanguage_inherit_dataset_values(
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
        model.LanguageStringTypeItem(
            languageCode="en",
            languageText="Persons in Sweden",
        ),
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


def test_variables_values_inherit_dataset_date_values_derived_from_path(
    metadata: Datadoc,
):
    state.metadata = metadata
    dataset_contains_data_from = "2021-10-10"
    setattr(
        state.metadata.dataset,
        DatasetIdentifiers.CONTAINS_DATA_FROM,
        dataset_contains_data_from,
    )
    set_variables_values_inherit_dataset_derived_date_values()
    for val in state.metadata.variables:
        assert metadata.dataset.contains_data_from == get_standard_metadata(
            metadata.variables_lookup[val.short_name],
            VariableIdentifiers.CONTAINS_DATA_FROM,
        )
    for val in state.metadata.variables:
        assert metadata.variables_lookup[val.short_name].contains_data_until is None
    setattr(
        state.metadata.variables_lookup["pers_id"],
        VariableIdentifiers.CONTAINS_DATA_FROM,
        "2011-10-10",
    )
    set_variables_values_inherit_dataset_derived_date_values()
    assert metadata.variables_lookup[
        "pers_id"
    ].contains_data_from != get_standard_metadata(
        metadata.dataset,
        DatasetIdentifiers.CONTAINS_DATA_FROM,
    )


def test_variables_values_inherit_dataset_date_values_not_when_variable_has_value(
    metadata: Datadoc,
):
    state.metadata = metadata
    dataset_contains_data_until = "2024-01-01"
    setattr(
        state.metadata.variables_lookup["pers_id"],
        VariableIdentifiers.CONTAINS_DATA_UNTIL,
        "2011-12-10",
    )
    setattr(
        state.metadata.dataset,
        DatasetIdentifiers.CONTAINS_DATA_UNTIL,
        dataset_contains_data_until,
    )
    set_variables_values_inherit_dataset_derived_date_values()
    assert metadata.variables_lookup[
        "pers_id"
    ].contains_data_until != get_standard_metadata(
        metadata.dataset,
        DatasetIdentifiers.CONTAINS_DATA_UNTIL,
    )


def test_variables_metadata_control_return_alert(metadata: Datadoc):
    """Return alert when obligatory metadata is missing."""
    state.metadata = metadata
    missing_metadata: str
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        state.metadata.write_metadata_document()
        if issubclass(w[1].category, ObligatoryVariableWarning):
            missing_metadata = str(w[1].message)
    result = variables_control(missing_metadata, metadata.variables)
    assert isinstance(result, dbc.Alert)


def test_variables_metadata_control_dont_return_alert(metadata: Datadoc):
    state.metadata = metadata
    missing_metadata: str | None = None
    for val in state.metadata.variables:
        """Not return alert when all obligatory metadata has value."""
        setattr(
            state.metadata.variables_lookup[val.short_name],
            VariableIdentifiers.NAME,
            model.LanguageStringType(
                [model.LanguageStringTypeItem(languageCode="nb", languageText="Test")],
            ),
        )
        setattr(
            state.metadata.variables_lookup[val.short_name],
            VariableIdentifiers.DATA_TYPE,
            enums.DataType.STRING,
        )
        setattr(
            state.metadata.variables_lookup[val.short_name],
            VariableIdentifiers.VARIABLE_ROLE,
            enums.VariableRole.MEASURE,
        )
        setattr(
            state.metadata.variables_lookup[val.short_name],
            VariableIdentifiers.DEFINITION_URI,
            "https://www.hat.com",
        )
        setattr(
            state.metadata.variables_lookup[val.short_name],
            VariableIdentifiers.IS_PERSONAL_DATA,
            enums.IsPersonalData.NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA,
        )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        state.metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryVariableWarning):
            missing_metadata = str(w[0].message)
    result = variables_control(missing_metadata, metadata.variables)
    assert result is None


def test_accept_variable_metadata_input_when_shortname_is_non_ascii(
    metadata_illegal_shortnames: Datadoc,
):
    state.metadata = metadata_illegal_shortnames
    assert metadata_illegal_shortnames.variables[-1].short_name == "rådyr"
    assert (
        accept_variable_metadata_input(
            "Format value",
            metadata_illegal_shortnames.variables[-1].short_name,
            metadata_field=VariableIdentifiers.FORMAT.value,
            language="nb",
        )
        is None
    )

    assert (
        getattr(state.metadata.variables[-1], VariableIdentifiers.FORMAT.value)
        == "Format value"
    )


@pytest.mark.parametrize(
    ("metadata_field", "value", "expected_model_value"),
    [
        (
            PseudoVariableIdentifiers.SHORT_NAME,
            "fnr",
            "fnr",
        ),
        (
            PseudoVariableIdentifiers.DATA_ELEMENT_PATH,
            "path",
            "path",
        ),
        (
            PseudoVariableIdentifiers.STABLE_IDENTIFIER_VERSION,
            "stable identifier",
            "stable identifier",
        ),
        (
            PseudoVariableIdentifiers.STABLE_IDENTIFIER_TYPE,
            "stable identifier type",
            "stable identifier type",
        ),
        (
            PseudoVariableIdentifiers.ENCRYPTION_ALGORITHM,
            "TINK-FPE",
            "TINK-FPE",
        ),
        (
            PseudoVariableIdentifiers.ENCRYPTION_KEY_REFERENCE,
            "SSB_GLOBAL_KEY_1",
            "SSB_GLOBAL_KEY_1",
        ),
        (
            PseudoVariableIdentifiers.SOURCE_VARIABLE,
            "fnr",
            "fnr",
        ),
        (
            PseudoVariableIdentifiers.SOURCE_DISPLAY_DATATYPE,
            "STRING",
            "STRING",
        ),
    ],
)
def test_accept_pseudo_variable_metadata_input_valid(
    metadata: Datadoc,
    metadata_field: PseudoVariableIdentifiers,
    value: MetadataInputTypes,
    expected_model_value: Any,  # noqa: ANN401
):
    state.metadata = metadata
    state.metadata.pseudo_variables = [model.PseudoVariable(short_name="fnr")]
    state.metadata._create_pseudo_variables_lookup()  # noqa: SLF001
    fnr_variable = metadata.pseudo_variables_lookup.get("fnr")
    assert fnr_variable is not None
    assert fnr_variable.short_name is not None
    assert (
        accept_pseudo_variable_metadata_input(
            value,
            fnr_variable.short_name,
            metadata_field=metadata_field.value,
        )
        is None
    )
    assert (
        getattr(state.metadata.pseudo_variables_lookup.get("fnr"), metadata_field.value)
        == expected_model_value
    )
