"""Test function build_edit_section."""

import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import model
from dash import html

from datadoc_editor.frontend.components.builders import build_edit_section
from datadoc_editor.frontend.fields.display_variables import VARIABLES_METADATA_LEFT
from datadoc_editor.frontend.fields.display_variables import VARIABLES_METADATA_RIGHT


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    [
        ([[], []], model.Variable()),
        (
            [VARIABLES_METADATA_LEFT, VARIABLES_METADATA_RIGHT],
            model.Variable(short_name="pers_id"),
        ),
    ],
)
def test_build_edit_section_return_correct_component(
    field_list,
    variable,
):
    """Assert method returns html section."""
    edit_section = build_edit_section(field_list, variable)
    assert isinstance(edit_section, html.Section)


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    [
        (
            [[], []],
            model.Variable(),
        ),
        (
            [VARIABLES_METADATA_LEFT, VARIABLES_METADATA_RIGHT],
            model.Variable(short_name="sivilstand"),
        ),
    ],
)
def test_build_edit_section_children_return_correct_components(
    field_list,
    variable,
):
    """Assert method has a list of children which returns SSB dash component and dash bootstrap Form."""
    edit_section = build_edit_section(field_list, variable)
    form = edit_section.children[1]
    assert isinstance(form, dbc.Form)


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    [
        ([[], []], model.Variable()),
        (
            [VARIABLES_METADATA_LEFT, VARIABLES_METADATA_RIGHT],
            model.Variable(short_name="sykepenger"),
        ),
    ],
)
def test_build_edit_section_has_correct_id(field_list, variable):
    """Assert dictionary id is build correctly with 'type' and."""
    edit_section = build_edit_section(field_list, variable)
    assert edit_section.id == {"type": "edit-section"}
