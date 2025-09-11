"""Test function build_dataset_edit_section."""

import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dapla_metadata.datasets import model
from dash import html

from datadoc_editor.frontend.components.builders import build_dataset_edit_section
from datadoc_editor.frontend.fields.display_dataset import DISPLAY_DATASET
from datadoc_editor.frontend.fields.display_dataset import (
    EDITABLE_DATASET_METADATA_LEFT,
)
from datadoc_editor.frontend.fields.display_dataset import (
    EDITABLE_DATASET_METADATA_RIGHT,
)
from datadoc_editor.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers

# List of obligatory and editable fields minus dropdowns with atypical options-getters
NON_ATYPICAL_DROPDOWNS = [
    m
    for m in DISPLAY_DATASET.values()
    if m.editable
    and m.identifier
    not in (
        DatasetIdentifiers.SUBJECT_FIELD.value,
        DatasetIdentifiers.OWNER.value,
    )
]

INPUT_DATA_BUILD_DATASET_SECTION = [
    (
        [NON_EDITABLE_DATASET_METADATA, []],
        model.Dataset(short_name="fantastic_dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
    (
        [[], []],
        model.Dataset(short_name="fantastic_dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
    (
        [[], []],
        None,
        {},
    ),
    (
        [[], []],
        None,
        {"type": "dataset-edit-section", "id": "obligatory-en"},
    ),
    (
        {},
        model.Dataset(short_name="last_dataset"),
        {},
    ),
    (
        [NON_ATYPICAL_DROPDOWNS, []],
        model.Dataset(),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
]


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("field_types", "dataset", "key"),
    INPUT_DATA_BUILD_DATASET_SECTION,
)
def test_build_dataset_section_is_html_section(
    field_types,
    dataset,
    key,
):
    edit_section = build_dataset_edit_section(
        field_types,
        dataset,
        key,
    )
    assert isinstance(edit_section, html.Section)
    assert edit_section._namespace == "dash_html_components"  # noqa: SLF001
    assert edit_section.id == key


@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.usefixtures("_statistic_subject_mapping_fake_subjects")
@pytest.mark.parametrize(
    (
        "edit_section",
        "expected_fields_left",
        "expected_fields_right",
    ),
    [
        (
            (
                [EDITABLE_DATASET_METADATA_LEFT, EDITABLE_DATASET_METADATA_RIGHT],
                model.Dataset(short_name="dataset"),
                {"type": "dataset-edit-section", "id": "dataset-nb"},
            ),
            6,
            8,
        ),
    ],
)
def test_build_dataset_edit_section_renders_ssb_components(
    edit_section,
    expected_fields_left,
    expected_fields_right,
):
    edit_section = build_dataset_edit_section(*edit_section)
    fields_left = edit_section.children[0].children
    fields_right = edit_section.children[1].children

    assert len(fields_left) == expected_fields_left
    assert len(fields_right) == expected_fields_right


NEW_INPUT_DATA_BUILD_DATASET_SECTION = [
    (
        [EDITABLE_DATASET_METADATA_LEFT, EDITABLE_DATASET_METADATA_RIGHT],
        model.Dataset(short_name="dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
    (
        [[], []],
        model.Dataset(short_name="dataset"),
        {"type": "dataset-edit-section", "id": "obligatory-nb"},
    ),
    (
        [[], []],
        None,
        {},
    ),
    (
        [[], []],
        None,
        {"type": "dataset-edit-section", "id": "obligatory-en"},
    ),
    (
        [[], []],
        model.Dataset(short_name="last_dataset"),
        {},
    ),
]


@pytest.mark.parametrize(
    ("field_types", "dataset", "key"),
    NEW_INPUT_DATA_BUILD_DATASET_SECTION,
)
@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.usefixtures("_statistic_subject_mapping_fake_subjects")
def test_build_dataset_edit_section_input_component_props(
    field_types,
    dataset,
    key,
):
    edit_section = build_dataset_edit_section(
        field_types,
        dataset,
        key,
    )
    fields = edit_section.children[0].children + edit_section.children[1].children

    input_components = [element for element in fields if isinstance(element, ssb.Input)]

    assert all(
        item.type in ("text", "url", "date", "number") for item in input_components
    )
    assert all(
        (
            item.debounce is True
            if item.type in ("text", "url")
            else item.debounce is False
        )
        for item in input_components
        if item.type != "number"
    )
    assert all(item.label != "" for item in input_components)


@pytest.mark.parametrize(
    ("field_types", "dataset", "key"),
    NEW_INPUT_DATA_BUILD_DATASET_SECTION,
)
@pytest.mark.usefixtures(
    "_code_list_fake_classifications",
    "_statistic_subject_mapping_fake_subjects",
)
def test_build_dataset_edit_section_dropdown_component_props(field_types, dataset, key):
    edit_section = build_dataset_edit_section(field_types, dataset, key)

    fields_left = edit_section.children[0].children
    fields_right = edit_section.children[1].children

    for fields in (fields_left, fields_right):
        dropdown_components = [
            element for element in fields if isinstance(element, ssb.Dropdown)
        ]
        assert all(item.items for item in dropdown_components)
        assert all(item.header for item in dropdown_components)
