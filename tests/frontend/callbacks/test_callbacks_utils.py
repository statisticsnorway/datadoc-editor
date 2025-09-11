import datetime
from dataclasses import dataclass
from unittest import mock

import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import model
from dash import html

from datadoc_editor import state
from datadoc_editor.frontend.callbacks.utils import check_variable_names
from datadoc_editor.frontend.callbacks.utils import find_existing_language_string
from datadoc_editor.frontend.callbacks.utils import render_tabs
from datadoc_editor.frontend.callbacks.utils import save_metadata_and_generate_alerts
from datadoc_editor.frontend.callbacks.utils import update_use_restriction_date
from datadoc_editor.frontend.callbacks.utils import update_use_restriction_type
from datadoc_editor.frontend.components.identifiers import ACCORDION_WRAPPER_ID
from datadoc_editor.frontend.components.identifiers import SECTION_WRAPPER_ID


def test_find_existing_language_string_no_existing_strings(bokmål_name: str):
    dataset_metadata = model.Dataset()
    assert find_existing_language_string(
        dataset_metadata,
        bokmål_name,
        "name",
        "nb",
    ) == model.LanguageStringType(
        [model.LanguageStringTypeItem(languageCode="nb", languageText=bokmål_name)],
    )


def test_find_existing_language_string_no_existing_strings_empty_value():
    dataset_metadata = model.Dataset()
    assert (
        find_existing_language_string(
            dataset_metadata,
            "",
            "name",
            "nb",
        )
        is None
    )


def test_find_existing_language_string_pre_existing_strings(
    english_name: str,
    bokmål_name: str,
    nynorsk_name: str,
    language_object: model.LanguageStringType,
):
    dataset_metadata = model.Dataset()
    dataset_metadata.name = language_object
    language_strings = find_existing_language_string(
        dataset_metadata,
        nynorsk_name,
        "name",
        "nn",
    )
    assert language_strings == model.LanguageStringType(
        [
            model.LanguageStringTypeItem(languageCode="en", languageText=english_name),
            model.LanguageStringTypeItem(languageCode="nb", languageText=bokmål_name),
            model.LanguageStringTypeItem(languageCode="nn", languageText=nynorsk_name),
        ],
    )


@pytest.mark.parametrize(
    ("tab", "identifier"),
    [
        ("dataset", SECTION_WRAPPER_ID),
        ("variables", ACCORDION_WRAPPER_ID),
    ],
)
def test_render_tabs(tab: str, identifier: str):
    result = render_tabs(tab)
    assert isinstance(result, html.Article)
    assert result.children[-1].id == identifier


def test_save_and_generate_alerts():
    mock_metadata = mock.Mock()

    @dataclass
    class Variable:
        short_name: str

    mock_metadata.variables = [
        Variable(short_name="var"),
        Variable(short_name="var illegal"),
    ]
    state.metadata = mock_metadata
    result = save_metadata_and_generate_alerts(
        mock_metadata,
    )
    assert (result[1] and result[2]) is None
    assert isinstance(result[0], dbc.Alert)
    assert isinstance(result[3], dbc.Alert)


@pytest.mark.parametrize(
    ("shortname"),
    [
        ("rådyr"),
        ("Var"),
        ("Var illegal"),
        ("V"),
    ],
)
def test_illegal_shortname(shortname: str):
    @dataclass
    class MockVariable:
        short_name: str

    mock_metadata = mock.Mock(variables=[MockVariable(short_name=shortname)])
    assert isinstance(check_variable_names(mock_metadata.variables), dbc.Alert)


@pytest.mark.parametrize(
    ("shortname"),
    [
        ("var"),
        ("var1"),
        ("var_2"),
    ],
)
def test_legal_shortname(shortname: str):
    @dataclass
    class MockVariable:
        short_name: str

    mock_metadata = mock.Mock(variables=[MockVariable(short_name=shortname)])
    assert check_variable_names(mock_metadata.variables) is None


@pytest.mark.parametrize(
    ("initial_value", "field", "index", "expected"),
    [
        (
            "DELETION_ANONYMIZATION",
            "type",
            0,
            model.UseRestrictionItem(
                use_restriction_type=model.UseRestrictionType.DELETION_ANONYMIZATION,
                use_restriction_date=None,
            ),
        ),
        (
            "PROCESS_LIMITATIONS",
            "type",
            0,
            model.UseRestrictionItem(
                use_restriction_type=model.UseRestrictionType.PROCESS_LIMITATIONS,
                use_restriction_date=None,
            ),
        ),
        (
            "2024-12-31",
            "date",
            1,
            model.UseRestrictionItem(
                use_restriction_type=None,
                use_restriction_date=datetime.date(2024, 12, 31),
            ),
        ),
        (
            "2025-12-31",
            "date",
            0,
            model.UseRestrictionItem(
                use_restriction_type=None,
                use_restriction_date=datetime.date(2025, 12, 31),
            ),
        ),
    ],
)
def test_update_use_restriction(initial_value, field, index, expected):
    dataset_metadata = model.Dataset()

    if index > 0:
        update_use_restriction_type(
            dataset_metadata, "DELETION_ANONYMIZATION", "use_restrictions", 0
        )

    if field == "type":
        result = update_use_restriction_type(
            dataset_metadata, initial_value, "use_restrictions", index
        )
    elif field == "date":
        result = update_use_restriction_date(
            dataset_metadata, initial_value, "use_restrictions", index
        )

    assert result[index] == expected


def test_find_existing_use_restriction_illegal_input():
    dataset_metadata = model.Dataset()
    with pytest.raises(ValueError, match="is not a valid UseRestrictionType"):
        update_use_restriction_type(
            dataset_metadata, "NOT_A_USE_RESTRICTION", "use_restrictions", 0
        )
