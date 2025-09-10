import pytest

from datadoc_editor import state
from datadoc_editor.frontend.fields.display_base import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.fields.display_variables import get_unit_type_options
from tests.conftest import CODE_LIST_DIR
from tests.utils import TEST_RESOURCES_DIRECTORY


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
