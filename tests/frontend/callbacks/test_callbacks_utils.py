from dataclasses import dataclass
from unittest import mock

import dash_bootstrap_components as dbc
import pytest
from dash import html
from datadoc_model.all_optional import model

from datadoc_editor import state
from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.callbacks.utils import check_variable_names
from datadoc_editor.frontend.callbacks.utils import find_existing_language_string
from datadoc_editor.frontend.callbacks.utils import map_dropdown_to_pseudo
from datadoc_editor.frontend.callbacks.utils import render_tabs
from datadoc_editor.frontend.callbacks.utils import save_metadata_and_generate_alerts
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
    ("variable", "expected_algorithm"),
    [
        (
            model.Variable(
                pseudonymization=model.Pseudonymization(
                    stable_identifier_type="FREG_SNR", encryption_algorithm="TINK-FPE"
                ),
            ),
            PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID,
        ),
        (
            model.Variable(pseudonymization=None),
            None,
        ),
        (
            model.Variable(
                pseudonymization=model.Pseudonymization(
                    encryption_algorithm="TINK-FPE"
                ),
            ),
            PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID,
        ),
        (
            model.Variable(
                pseudonymization=model.Pseudonymization(
                    encryption_algorithm="TINK-DAED",
                ),
            ),
            PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA,
        ),
        (
            model.Variable(
                pseudonymization=model.Pseudonymization(
                    encryption_algorithm="TINK_PPP",
                ),
            ),
            PseudonymizationAlgorithmsEnum.CUSTOM,
        ),
        (
            model.Variable(
                pseudonymization=model.Pseudonymization(
                    encryption_key_reference="custom-common-key-1",
                ),
            ),
            None,
        ),
    ],
    ids=[
        "papis_with_stable_id",
        "without_pseudonymization",
        "papis_without_stable_id",
        "standard_algorithm_dapla",
        "custom_algorithm",
        "not_encryption_algorithm",
    ],
)
def test_map_dropdown_value(variable: model.Variable, expected_algorithm: str):
    assert map_dropdown_to_pseudo(variable) == expected_algorithm
