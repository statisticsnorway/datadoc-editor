import pytest

from datadoc_editor import state
from datadoc_editor.frontend.constants import DELETE_SELECTED
from datadoc_editor.frontend.constants import DESELECT
from datadoc_editor.frontend.constants import DROPDOWN_DELETE_OPTION
from datadoc_editor.frontend.constants import DROPDOWN_DESELECT_OPTION
from datadoc_editor.frontend.constants import NUM_GLOBAL_EDITABLE_VARIABLES
from datadoc_editor.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc_editor.frontend.fields.display_variables import (
    GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME,
)
from datadoc_editor.frontend.fields.display_variables import GLOBAL_VARIABLES
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers
from datadoc_editor.frontend.fields.display_variables import get_unit_type_options
from datadoc_editor.frontend.fields.display_variables import (
    get_unit_type_options_with_delete,
)
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


@pytest.mark.parametrize(
    ("code_list_csv_filepath_nb", "expected"),
    [
        (
            TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv",
            [
                {"title": DROPDOWN_DESELECT_OPTION, "id": DESELECT},
                {"title": DROPDOWN_DELETE_OPTION, "id": DELETE_SELECTED},
                {"title": "Adresse", "id": "01"},
                {"title": "Arbeidsulykke", "id": "02"},
                {"title": "Bolig", "id": "03"},
            ],
        ),
    ],
)
def test_get_unit_type_options_with_delete_and_deselect(
    code_list_fake_structure,
    expected,
):
    state.unit_types = code_list_fake_structure
    state.unit_types.wait_for_external_result()
    assert get_unit_type_options_with_delete() == expected


def test_global():
    assert len(GLOBAL_VARIABLES) == NUM_GLOBAL_EDITABLE_VARIABLES


def test_global_tuple():
    assert (
        DISPLAY_VARIABLES[VariableIdentifiers.UNIT_TYPE].identifier,
        DISPLAY_VARIABLES[VariableIdentifiers.UNIT_TYPE].display_name,
    ) in GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME
