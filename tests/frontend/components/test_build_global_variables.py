import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb
from dash import html

from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_edit_section,
)
from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_input_field_section,
)
from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_ssb_accordion,
)
from datadoc_editor.frontend.constants import GLOBAL_HEADER
from datadoc_editor.frontend.fields.display_variables import GLOBAL_VARIABLES


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_build_global_edit_section():
    global_edit_section = build_global_edit_section(GLOBAL_VARIABLES, {})
    assert isinstance(global_edit_section, html.Section)


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_build_global_input_section():
    global_input_section = build_global_input_field_section(GLOBAL_VARIABLES, {})
    assert isinstance(global_input_section, dbc.Form)


def test_build_global_variables_accordion():
    global_accordion = build_global_ssb_accordion(
        GLOBAL_HEADER, {"id": "global_id", "type": "accordion"}, ssb.Paragraph
    )
    assert isinstance(global_accordion, ssb.Accordion)
    assert isinstance(global_accordion.children[0], html.Section)
    assert global_accordion.header == GLOBAL_HEADER
