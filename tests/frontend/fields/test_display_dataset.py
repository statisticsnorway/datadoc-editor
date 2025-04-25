import pytest

from datadoc_editor import state
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_dataset import (
    get_statistical_subject_options,
)
from datadoc_editor.frontend.fields.display_dataset import get_unit_type_options
from tests.conftest import CODE_LIST_DIR
from tests.conftest import STATISTICAL_SUBJECT_STRUCTURE_DIR
from tests.utils import TEST_RESOURCES_DIRECTORY


@pytest.mark.parametrize(
    ("subject_xml_file_path", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY
            / STATISTICAL_SUBJECT_STRUCTURE_DIR
            / "extract_secondary_subject.xml",
            [
                {"title": DROPDOWN_DESELECT_OPTION, "id": ""},
                {"title": "aa norwegian - aa00 norwegian", "id": "aa00"},
                {"title": "aa norwegian - aa01 norwegian", "id": "aa01"},
                {"title": "ab norwegian - ab00 norwegian", "id": "ab00"},
                {"title": "ab norwegian - ab01 norwegian", "id": "ab01"},
            ],
        ),
        (
            TEST_RESOURCES_DIRECTORY
            / STATISTICAL_SUBJECT_STRUCTURE_DIR
            / "missing_language.xml",
            [
                {"title": DROPDOWN_DESELECT_OPTION, "id": ""},
                {"title": " - aa00 norwegian", "id": "aa00"},
                {"title": " - aa01 norwegian", "id": "aa01"},
                {"title": " - ab00 norwegian", "id": "ab00"},
                {"title": " - ", "id": "ab01"},
            ],
        ),
    ],
)
def test_get_statistical_subject_options(
    subject_mapping_fake_statistical_structure,
    expected,
):
    state.statistic_subject_mapping = subject_mapping_fake_statistical_structure
    state.statistic_subject_mapping.wait_for_external_result()
    assert get_statistical_subject_options() == expected


@pytest.mark.parametrize(
    ("code_list_csv_filepath_nb", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv",
            [
                {"title": DROPDOWN_DESELECT_OPTION, "id": ""},
                {"title": "Adresse", "id": "01"},
                {"title": "Arbeidsulykke", "id": "02"},
                {"title": "Bolig", "id": "03"},
            ],
        ),
    ],
)
def test_get_unit_type_options(
    code_list_fake_structure,
    expected,
):
    state.unit_types = code_list_fake_structure
    state.unit_types.wait_for_external_result()
    assert get_unit_type_options() == expected
