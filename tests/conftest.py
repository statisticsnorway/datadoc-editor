"""Shared fixtures and configuration."""

from __future__ import annotations

import concurrent
import copy
import functools
import logging
import os
import pathlib
import shutil
from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from bs4 import ResultSet
from dapla_metadata.dapla.user_info import TestUserInfo  # type:ignore [import-untyped]
from dapla_metadata.datasets import Datadoc
from dapla_metadata.datasets import model
from dapla_metadata.datasets.code_list import CodeList
from dapla_metadata.datasets.statistic_subject_mapping import StatisticSubjectMapping

from datadoc_editor import state

from .utils import TEST_EXISTING_METADATA_DIRECTORY
from .utils import TEST_PARQUET_FILE_NAME
from .utils import TEST_PARQUET_FILE_NAME_ILLEGAL_SHORTNAMES
from .utils import TEST_PARQUET_FILEPATH
from .utils import TEST_PARQUET_FILEPATH_ILLEGAL_SHORTNAMES
from .utils import TEST_RESOURCES_DIRECTORY

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

logging.getLogger("faker").setLevel(logging.ERROR)

DATADOC_METADATA_MODULE = "dapla_metadata.datasets"
CODE_LIST_DIR = "code_list"
STATISTICAL_SUBJECT_STRUCTURE_DIR = "statistical_subject_structure"


@pytest.fixture(autouse=True)
def _clear_environment(mocker: MockerFixture) -> None:
    """Ensure that the environment is cleared."""
    mocker.patch.dict(os.environ, clear=True)


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["no_NO"]


@pytest.fixture
def dummy_timestamp() -> datetime:
    return datetime(2022, 1, 1, tzinfo=UTC)


@pytest.fixture
def _mock_timestamp(mocker: MockerFixture, dummy_timestamp: datetime) -> None:
    mocker.patch(
        DATADOC_METADATA_MODULE + ".core.get_timestamp_now",
        return_value=dummy_timestamp,
    )


@pytest.fixture
def _mock_user_info(mocker: MockerFixture) -> None:
    mocker.patch(
        "dapla_metadata.dapla.user_info.get_user_info_for_current_platform",
        return_value=TestUserInfo(),
    )


@pytest.fixture
def metadata(
    _mock_timestamp: None,
    _mock_user_info: None,
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    tmp_path: Path,
) -> Datadoc:
    shutil.copy(TEST_PARQUET_FILEPATH, tmp_path / TEST_PARQUET_FILE_NAME)
    return Datadoc(
        str(tmp_path / TEST_PARQUET_FILE_NAME),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
    )


@pytest.fixture
def metadata_illegal_shortnames(
    _mock_timestamp: None,
    _mock_user_info: None,
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    tmp_path: Path,
) -> Datadoc:
    shutil.copy(
        TEST_PARQUET_FILEPATH_ILLEGAL_SHORTNAMES,
        tmp_path / TEST_PARQUET_FILE_NAME_ILLEGAL_SHORTNAMES,
    )
    return Datadoc(
        str(tmp_path / TEST_PARQUET_FILE_NAME_ILLEGAL_SHORTNAMES),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
    )


@pytest.fixture
def existing_metadata_path() -> Path:
    return TEST_EXISTING_METADATA_DIRECTORY


@pytest.fixture(autouse=True)
def _clear_state() -> None:
    """Global fixture, referred to in pytest.ini."""
    try:
        del state.metadata
        del state.statistic_subject_mapping
    except AttributeError:
        pass


@pytest.fixture
def english_name() -> str:
    return "English Name"


@pytest.fixture
def bokmål_name() -> str:
    return "Bokmål navn"


@pytest.fixture
def nynorsk_name() -> str:
    return "Nynorsk namn"


@pytest.fixture
def language_object(
    english_name: str,
    bokmål_name: str,
    nynorsk_name: str,
) -> model.LanguageStringType:
    return model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="en", languageText=english_name),
            model.LanguageStringTypeItem(languageCode="nb", languageText=bokmål_name),
            model.LanguageStringTypeItem(languageCode="nn", languageText=nynorsk_name),
        ],
    )


@pytest.fixture
def full_dataset_state_path(
    path_parts_to_insert: str | list[str],
) -> pathlib.Path:
    """Create a longer path structure from just one section.

    Examples:
    >>> full_dataset_state_path('inndata')
    'tests/inndata/resources/person_data_v1.parquet'
    >>> full_dataset_state_path(['klargjorte_data', 'arbmark'])
    'tests/klargjorte_data/arbmark/resources/person_data_v1.parquet'
    """
    split_path = list(pathlib.Path(TEST_PARQUET_FILEPATH).parts)
    new_path = copy.copy(split_path)

    if isinstance(path_parts_to_insert, str):
        parts = [path_parts_to_insert]
    else:
        parts = path_parts_to_insert
    for p in parts:
        new_path.insert(-2, p)
    return pathlib.Path().joinpath(*new_path)


@pytest.fixture
def subject_xml_file_path() -> pathlib.Path:
    return (
        TEST_RESOURCES_DIRECTORY
        / STATISTICAL_SUBJECT_STRUCTURE_DIR
        / "extract_secondary_subject.xml"
    )


@pytest.fixture
def thread_pool_executor() -> concurrent.futures.ThreadPoolExecutor:
    return concurrent.futures.ThreadPoolExecutor(max_workers=12)


@pytest.fixture
def subject_mapping_fake_statistical_structure(
    _mock_fetch_statistical_structure,
    thread_pool_executor,
) -> StatisticSubjectMapping:
    return StatisticSubjectMapping(thread_pool_executor, "placeholder")


@pytest.fixture
def _mock_fetch_statistical_structure(
    mocker,
    subject_xml_file_path: pathlib.Path,
) -> None:
    def fake_statistical_structure() -> ResultSet:
        with subject_xml_file_path.open() as f:
            return BeautifulSoup(f.read(), features="xml").find_all("hovedemne")

    mocker.patch(
        DATADOC_METADATA_MODULE
        + ".statistic_subject_mapping.StatisticSubjectMapping._fetch_data_from_external_source",
        functools.partial(fake_statistical_structure),
    )


@pytest.fixture
def _statistic_subject_mapping_fake_subjects(
    subject_mapping_fake_statistical_structure,
) -> None:
    state.statistic_subject_mapping = subject_mapping_fake_statistical_structure
    state.statistic_subject_mapping.wait_for_external_result()


@pytest.fixture
def subject_mapping_http_exception(
    requests_mock,
    exception_to_raise,
    thread_pool_executor,
) -> StatisticSubjectMapping:
    requests_mock.get(
        "http://test.some.url.com",
        exc=exception_to_raise,
    )
    return StatisticSubjectMapping(thread_pool_executor, "http://test.some.url.com")


@pytest.fixture
def code_list_csv_filepath_nb() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv"


@pytest.fixture
def code_list_csv_filepath_nn() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nn.csv"


@pytest.fixture
def code_list_csv_filepath_en() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_en.csv"


@pytest.fixture
def _mock_fetch_dataframe(
    mocker,
    code_list_csv_filepath_nb: pathlib.Path,
    code_list_csv_filepath_nn: pathlib.Path,
    code_list_csv_filepath_en: pathlib.Path,
) -> None:
    def fake_code_list() -> dict[str, pd.DataFrame]:
        return {
            "nb": pd.read_csv(code_list_csv_filepath_nb, converters={"code": str}),
            "nn": pd.read_csv(code_list_csv_filepath_nn, converters={"code": str}),
            "en": pd.read_csv(code_list_csv_filepath_en, converters={"code": str}),
        }

    mocker.patch(
        DATADOC_METADATA_MODULE
        + ".code_list.CodeList._fetch_data_from_external_source",
        functools.partial(fake_code_list),
    )


@pytest.fixture
def code_list_fake_structure(_mock_fetch_dataframe, thread_pool_executor) -> CodeList:
    return CodeList(thread_pool_executor, 100)


@pytest.fixture
def _code_list_fake_classifications(code_list_fake_structure) -> None:
    state.measurement_units = code_list_fake_structure
    state.measurement_units.wait_for_external_result()

    state.data_sources = code_list_fake_structure
    state.data_sources.wait_for_external_result()

    state.unit_types = code_list_fake_structure
    state.unit_types.wait_for_external_result()

    state.organisational_units = code_list_fake_structure
    state.organisational_units.wait_for_external_result()

    state.measurement_units = code_list_fake_structure
    state.measurement_units.wait_for_external_result()


@pytest.fixture
def copy_dataset_to_path(
    tmp_path: pathlib.Path,
    full_dataset_state_path: pathlib.Path,
) -> pathlib.Path:
    temporary_dataset = tmp_path / full_dataset_state_path
    temporary_dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(TEST_PARQUET_FILEPATH, temporary_dataset)
    return temporary_dataset
