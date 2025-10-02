import ssb_dash_components as ssb
from dash import html

from datadoc_editor.frontend.components.global_variables_builders import (
    build_global_ssb_accordion,
)
from datadoc_editor.frontend.fields.display_global_variables import GLOBAL_HEADER


def test_build_global_edit_section():
    pass


def test_build_global_variables_accordion():
    global_accordion = build_global_ssb_accordion(
        GLOBAL_HEADER, {"id": "global_id", "type": "accordion"}, ssb.Paragraph
    )
    assert isinstance(global_accordion, ssb.Accordion)
    assert isinstance(global_accordion.children[0], html.Section)
    assert global_accordion.header == GLOBAL_HEADER
