from __future__ import annotations

import datetime
import random
import warnings
from typing import TYPE_CHECKING
from unittest.mock import Mock
from unittest.mock import patch
from uuid import UUID

import dash
import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import ObligatoryDatasetWarning
from dapla_metadata.datasets import model

from datadoc_editor import enums
from datadoc_editor import state
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_metadata_date_input
from datadoc_editor.frontend.callbacks.dataset import accept_dataset_metadata_input
from datadoc_editor.frontend.callbacks.dataset import open_dataset_handling
from datadoc_editor.frontend.callbacks.dataset import process_special_cases
from datadoc_editor.frontend.callbacks.utils import dataset_control
from datadoc_editor.frontend.constants import INVALID_DATE_ORDER
from datadoc_editor.frontend.constants import INVALID_VALUE
from datadoc_editor.frontend.fields.display_dataset import DISPLAY_DATASET
from datadoc_editor.frontend.fields.display_dataset import (
    MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS,
)
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers

if TYPE_CHECKING:
    from dapla_metadata.datasets import Datadoc

    from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes

DATASET_CALLBACKS_MODULE = "datadoc_editor.frontend.callbacks.dataset"


@pytest.fixture
def n_clicks_1():
    return 1


@pytest.fixture
def file_path():
    return "valid/path/to/file.json"


@pytest.fixture
def file_path_without_dates():
    return "valid/path/to/person_data_v1.parquet"


@pytest.mark.parametrize(
    ("metadata_identifier", "provided_value", "expected_model_value"),
    [
        (DatasetIdentifiers.SHORT_NAME, "person_data_v1", "person_data_v1"),
        (
            DatasetIdentifiers.ASSESSMENT,
            enums.Assessment.PROTECTED,
            enums.Assessment.PROTECTED.value,
        ),
        (
            DatasetIdentifiers.DATASET_STATUS,
            enums.DataSetStatus.INTERNAL,
            enums.DataSetStatus.INTERNAL.value,
        ),
        (
            DatasetIdentifiers.DATASET_STATE,
            enums.DataSetState.INPUT_DATA,
            enums.DataSetState.INPUT_DATA.value,
        ),
        (
            DatasetIdentifiers.NAME,
            "Dataset name",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Dataset name",
                    ),
                ],
            ),
        ),
        (
            DatasetIdentifiers.DESCRIPTION,
            "Dataset description",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Dataset description",
                    ),
                ],
            ),
        ),
        (
            DatasetIdentifiers.DATA_SOURCE,
            "Census",
            "Census",
        ),
        (
            DatasetIdentifiers.POPULATION_DESCRIPTION,
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
        (DatasetIdentifiers.VERSION, 1, "1"),
        (
            DatasetIdentifiers.VERSION_DESCRIPTION,
            "Version description",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Version description",
                    ),
                ],
            ),
        ),
        (
            DatasetIdentifiers.UNIT_TYPE,
            "17",
            "17",
        ),
        (
            DatasetIdentifiers.TEMPORALITY_TYPE,
            enums.TemporalityTypeType.ACCUMULATED,
            enums.TemporalityTypeType.ACCUMULATED.value,
        ),
        (
            DatasetIdentifiers.SUBJECT_FIELD,
            "al03",
            "al03",
        ),
        (
            DatasetIdentifiers.KEYWORD,
            "one,two,three",
            ["one", "two", "three"],
        ),
        (
            DatasetIdentifiers.SPATIAL_COVERAGE_DESCRIPTION,
            "Spatial coverage description",
            model.LanguageStringType(
                [
                    model.LanguageStringTypeItem(
                        languageCode="nb",
                        languageText="Spatial coverage description",
                    ),
                    model.LanguageStringTypeItem(
                        languageCode="nn",
                        languageText="Noreg",
                    ),
                    model.LanguageStringTypeItem(
                        languageCode="en",
                        languageText="Norway",
                    ),
                ],
            ),
        ),
        (DatasetIdentifiers.CONTAINS_PERSONAL_DATA, True, True),
        (
            DatasetIdentifiers.USE_RESTRICTION,
            enums.UseRestriction.PROCESS_LIMITATIONS,
            "PROCESS_LIMITATIONS",
        ),
        (
            DatasetIdentifiers.USE_RESTRICTION_DATE,
            "2024-12-31T23:59:59Z",
            datetime.datetime(
                2024,
                12,
                31,
                23,
                59,
                59,
                tzinfo=datetime.UTC,
            ),
        ),
        (
            DatasetIdentifiers.ID,
            "2f72477a-f051-43ee-bf8b-0d8f47b5e0a7",
            UUID("2f72477a-f051-43ee-bf8b-0d8f47b5e0a7"),
        ),
        (
            DatasetIdentifiers.OWNER,
            "Seksjon for dataplattform",
            "Seksjon for dataplattform",
        ),
    ],
)
def test_accept_dataset_metadata_input_valid_data(
    metadata_identifier: DatasetIdentifiers,
    provided_value: MetadataInputTypes,
    expected_model_value: str,
    metadata: Datadoc,
):
    state.metadata = metadata
    output = accept_dataset_metadata_input(provided_value, metadata_identifier, "nb")
    assert output[0] is False
    assert output[1] == ""
    assert (
        getattr(state.metadata.dataset, metadata_identifier.value)
        == expected_model_value
    )


def test_accept_dataset_metadata_input_incorrect_data_type(metadata: Datadoc):
    state.metadata = metadata
    output = accept_dataset_metadata_input(
        3.1415,
        DatasetIdentifiers.DATASET_STATE.value,
        "",
    )
    assert output[0] is True
    assert output[1] == INVALID_VALUE


earlier = str(datetime.date(2020, 1, 1))
later = str(datetime.date(2024, 1, 1))


@pytest.mark.parametrize(
    ("start_date", "end_date", "expect_error"),
    [
        (None, None, False),
        (later, None, False),
        (None, earlier, False),
        (earlier, earlier, False),
        (earlier, later, False),
        (later, earlier, True),
        (None, "12th March 1953", True),
    ],
    ids=[
        "no-input",
        "start-date-only",
        "end-date-only",
        "identical-dates",
        "correct-order",
        "incorrect-order",
        "invalid-date-format",
    ],
)
def test_accept_dataset_metadata_input_date_validation(
    metadata: Datadoc,
    start_date: str | None,
    end_date: str | None,
    expect_error: bool,  # noqa: FBT001
):
    state.metadata = metadata
    output = accept_dataset_metadata_date_input(
        DatasetIdentifiers.CONTAINS_DATA_UNTIL,
        start_date,
        end_date,
    )
    assert output[2] is expect_error
    if expect_error:
        assert output[3] == INVALID_DATE_ORDER.format(
            contains_data_from_display_name=DISPLAY_DATASET[
                DatasetIdentifiers.CONTAINS_DATA_FROM
            ].display_name,
            contains_data_until_display_name=DISPLAY_DATASET[
                DatasetIdentifiers.CONTAINS_DATA_UNTIL
            ].display_name,
        )
    else:
        assert output[1] == ""
        assert output[3] == ""


@pytest.mark.parametrize(
    "path",
    [
        "tests/resources/datasets/ifpn/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "  tests/resources/datasets/ifpn/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet  ",
    ],
)
@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_normal(
    open_file_mock: Mock,  # noqa: ARG001
    n_clicks_1: int,
    path: str,
):
    alert, counter = open_dataset_handling(
        n_clicks_1,
        path,
        0,
    )
    assert alert.color == "success"
    assert counter == 1


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_file_not_found(
    open_file_mock: Mock,
    n_clicks_1: int,
    file_path: str,
):
    open_file_mock.side_effect = FileNotFoundError()

    alert, counter = open_dataset_handling(
        n_clicks_1,
        file_path,
        0,
    )
    assert alert.color == "danger"
    assert counter == dash.no_update


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_general_exception(
    open_file_mock: Mock,
    n_clicks_1: int,
    file_path: str,
):
    open_file_mock.side_effect = ValueError()

    alert, counter = open_dataset_handling(
        n_clicks_1,
        file_path,
        0,
    )
    assert alert.color == "danger"
    assert counter == dash.no_update


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_no_click(
    open_file_mock: Mock,  # noqa: ARG001
    file_path: str,
):
    alert, counter = open_dataset_handling(
        0,
        file_path,
        0,
    )
    assert alert
    assert counter == 1


@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
def test_open_dataset_handling_naming_standard(
    open_file_mock: Mock,  # noqa: ARG001
    n_clicks_1: int,
    file_path_without_dates: str,
):
    alert, counter = open_dataset_handling(
        n_clicks_1,
        file_path_without_dates,
        0,
    )
    assert alert.color == "warning"
    assert counter == 1


@patch(f"{DATASET_CALLBACKS_MODULE}.DaplaDatasetPathInfo")
@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
@patch(
    f"{DATASET_CALLBACKS_MODULE}.set_variables_values_inherit_dataset_derived_date_values"
)
def test_open_dataset_handling_metadata_inconsistency(
    set_vars_mock: Mock,  # noqa: ARG001
    open_file_mock: Mock,
    path_info_mock: Mock,
):
    path_info_mock.return_value.path_complies_with_naming_standard.return_value = True
    mock_metadata = Mock()
    mock_metadata.dataset_consistency_status = [
        {"name": "Bucket name", "success": True},
        {"name": "Data product name", "success": True},
        {"name": "Dataset state", "success": False},
        {"name": "Dataset short name", "success": True},
        {"name": "Variable names", "success": True},
        {"name": "Variable datatypes", "success": True},
    ]
    open_file_mock.return_value = mock_metadata
    alert, counter = open_dataset_handling(
        n_clicks=1,
        file_path="dummy/path.parquet",
        dataset_opened_counter=0,
    )
    assert alert.color == "warning"
    assert counter == 1
    assert "Det er inkonsistens mellom data og metadata for" in str(alert)


@patch(f"{DATASET_CALLBACKS_MODULE}.DaplaDatasetPathInfo")
@patch(f"{DATASET_CALLBACKS_MODULE}.open_file")
@patch(
    f"{DATASET_CALLBACKS_MODULE}.set_variables_values_inherit_dataset_derived_date_values"
)
def test_open_dataset_handling_no_metadata_inconsistency(
    set_vars_mock: Mock,  # noqa: ARG001
    open_file_mock: Mock,
    path_info_mock: Mock,
):
    path_info_mock.return_value.path_complies_with_naming_standard.return_value = True
    mock_metadata = Mock()
    mock_metadata.dataset_consistency_status = [
        {"name": "Bucket name", "success": True},
        {"name": "Data product name", "success": True},
        {"name": "Dataset state", "success": True},
        {"name": "Dataset short name", "success": True},
        {"name": "Variable names", "success": True},
        {"name": "Variable datatypes", "success": True},
    ]
    open_file_mock.return_value = mock_metadata
    alert, counter = open_dataset_handling(
        n_clicks=1,
        file_path="dummy/path.parquet",
        dataset_opened_counter=0,
    )
    assert alert.color == "success"
    assert counter == 1
    assert "Åpnet dataset" in str(alert)


def test_process_special_cases_keyword():
    value = "test,key,words"
    identifier = "keyword"
    expected = ["test", "key", "words"]
    assert process_special_cases(value, identifier) == expected


@patch(f"{DATASET_CALLBACKS_MODULE}.find_existing_language_string")
def test_process_special_cases_language_string(
    mock_find: Mock,
    metadata: Datadoc,
):
    state.metadata = metadata
    language = "en"
    value = "Test language string"
    identifier = random.choice(  # noqa: S311
        MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS,
    )
    expected = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="Existing language string",
            ),
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=value,
            ),
        ],
    )
    mock_find.return_value = expected

    assert process_special_cases(value, identifier, language) == expected


def test_process_special_cases_no_change():
    value = ["unchanged", "values"]
    identifier = "random"
    assert process_special_cases(value, identifier) == value


def test_dataset_metadata_control_return_alert(metadata: Datadoc):
    """Return alert when obligatory metadata is missing."""
    state.metadata = metadata
    missing_metadata: str
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        state.metadata.write_metadata_document()
        if issubclass(w[0].category, ObligatoryDatasetWarning):
            missing_metadata = str(w[0].message)
    result = dataset_control(missing_metadata)
    assert isinstance(result, dbc.Alert)


def test_dataset_metadata_control_not_return_alert():
    missing_metadata = None
    result = dataset_control(missing_metadata)
    assert result is None
