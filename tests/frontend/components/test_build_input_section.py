"""Test function build_input_field_section."""

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dapla_metadata.datasets import model

from datadoc_editor.frontend.components.builders import build_input_field_section
from datadoc_editor.frontend.components.builders import (
    build_variables_pseudonymization_section,
)
from datadoc_editor.frontend.fields.display_base import MetadataCheckboxField
from datadoc_editor.frontend.fields.display_base import MetadataDropdownField
from datadoc_editor.frontend.fields.display_base import MetadataInputField
from datadoc_editor.frontend.fields.display_base import MetadataPeriodField
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_METADATA,
)
from datadoc_editor.frontend.fields.display_variables import VARIABLES_METADATA_LEFT
from datadoc_editor.frontend.fields.display_variables import VARIABLES_METADATA_RIGHT

VARIABLES_METADATA = VARIABLES_METADATA_LEFT + VARIABLES_METADATA_RIGHT

INPUT_FIELD_SECTION = [
    (
        VARIABLES_METADATA,
        model.Variable(short_name="hoveddiagnose"),
    ),
    (
        VARIABLES_METADATA,
        model.Variable(short_name="pers_id"),
    ),
    (
        VARIABLES_METADATA,
        model.Variable(short_name="ber_bruttoformue"),
    ),
    (
        VARIABLES_METADATA,
        model.Variable(short_name="sykepenger"),
    ),
]


@pytest.mark.usefixtures("_code_list_fake_classifications")
def test_build_input_field_section_no_input():
    """Assert build with empty inputs returns dash bootstrap Form component and empty children list."""
    input_section = build_input_field_section(
        [],
        "",
        "",
    )
    assert input_section.children == []
    assert isinstance(input_section, dbc.Form)


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_input_components(
    field_list,
    variable,
):
    input_section = build_input_field_section(field_list, "left", variable)

    elements_of_input = [
        element for element in input_section.children if isinstance(element, ssb.Input)
    ]

    elements_of_input_and_type_text_url = [
        element
        for element in elements_of_input
        if element.type in {"text", "url", "number"}
    ]

    variable_identifier_input = [
        element
        for element in VARIABLES_METADATA
        if isinstance(element, MetadataInputField)
    ]

    assert all(isinstance(field, ssb.Input) for field in elements_of_input)
    assert all(item.debounce is True for item in elements_of_input_and_type_text_url)
    assert all(
        item1.label == item2.display_name
        for item1, item2 in zip(
            elements_of_input_and_type_text_url,
            variable_identifier_input,
            strict=False,
        )
    )


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_checkbox_components(
    field_list,
    variable,
):
    """Test checkbox fields for variabel identifiers."""
    input_section = build_input_field_section(field_list, "left", variable)
    elements_of_checkbox = [
        element
        for element in input_section.children
        if isinstance(element, ssb.Checkbox)
    ]

    variable_identifier_checkbox = [
        element
        for element in VARIABLES_METADATA
        if isinstance(element, MetadataCheckboxField)
    ]

    assert all(isinstance(item, ssb.Checkbox) for item in elements_of_checkbox)
    assert all(item.disabled is False for item in elements_of_checkbox)
    assert all(item._type == "Checkbox" for item in elements_of_checkbox)  # noqa: SLF001
    assert all(
        item1.label == item2.display_name
        for item1, item2 in zip(
            elements_of_checkbox,
            variable_identifier_checkbox,
            strict=False,
        )
    )


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_type_date(field_list, variable):
    """Test Input field type 'url'."""
    input_section = build_input_field_section(field_list, "left", variable)

    elements_of_input = [
        element for element in input_section.children if isinstance(element, ssb.Input)
    ]

    elements_of_date = [
        element for element in elements_of_input if element.type == "date"
    ]

    variable_identifier_date = [
        element for element in field_list if isinstance(element, MetadataPeriodField)
    ]

    assert all(
        item1.label == item2.display_name
        for item1, item2 in zip(
            elements_of_date,
            variable_identifier_date,
            strict=False,
        )
    )
    assert all(item.debounce is False for item in elements_of_date)


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_type_url(field_list, variable):
    input_section = build_input_field_section(field_list, "right", variable)
    variable_identifier_input = [
        element for element in field_list if isinstance(element, MetadataInputField)
    ]
    variable_identifier_url = [
        element for element in variable_identifier_input if element.type == "url"
    ]
    elements_of_input_and_type_url = [
        element
        for element in input_section.children
        if isinstance(element, ssb.Input) and element.type == "url"
    ]
    assert all(item.debounce is True for item in elements_of_input_and_type_url)
    for item1, item2 in zip(
        elements_of_input_and_type_url,
        variable_identifier_url,
        strict=False,
    ):
        assert item1.label == item2.display_name


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    INPUT_FIELD_SECTION,
)
def test_build_input_fields_dropdown_components(
    field_list,
    variable,
):
    """Test props for variable identifiers fields."""
    input_section = build_input_field_section(field_list, "right", variable)
    type_dropdown = ssb.Dropdown
    elements_of_dropdown = [
        element
        for element in input_section.children
        if isinstance(element, type_dropdown)
    ]
    variable_identifier_dropdown = [
        element for element in field_list if isinstance(element, MetadataDropdownField)
    ]
    assert all(isinstance(item, type_dropdown) for item in elements_of_dropdown)
    for item in elements_of_dropdown:
        assert item._type == "Dropdown"  # noqa: SLF001
    for item1, item2 in zip(
        elements_of_dropdown,
        variable_identifier_dropdown,
        strict=False,
    ):
        assert item1.header == item2.display_name
    for item1, item2 in zip(
        elements_of_dropdown,
        variable_identifier_dropdown,
        strict=False,
    ):
        assert item1.items == item2.options_getter()


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_list", "variable"),
    INPUT_FIELD_SECTION,
)
def test_build_pseudo_input_section(
    field_list,
    variable,
):
    input_section = build_variables_pseudonymization_section(
        field_list, "left", variable
    )

    elements_of_input = [
        element for element in input_section.children if isinstance(element, ssb.Input)
    ]

    variable_identifier_input = [
        element
        for element in PSEUDONYMIZATION_METADATA
        if isinstance(element, MetadataInputField)
    ]

    assert all(isinstance(field, ssb.Input) for field in elements_of_input)
    assert all(item.debounce is True for item in elements_of_input)
    assert all(
        item1.label == item2.display_name
        for item1, item2 in zip(
            elements_of_input,
            variable_identifier_input,
            strict=False,
        )
    )
