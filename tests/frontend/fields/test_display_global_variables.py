from datadoc_editor.frontend.fields.display_global_variables import (
    GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME,
)
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_VARIABLES


def test_global():
    num_globals = 6
    assert len(GLOBAL_VARIABLES) == num_globals


def test_global_tuple():
    assert GLOBAL_EDITABLE_VARIABLES_METADATA_AND_DISPLAY_NAME[0][1] == "Enhetstype"
