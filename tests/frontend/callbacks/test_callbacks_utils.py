import datetime
from dataclasses import dataclass
from unittest import mock

import dash_bootstrap_components as dbc
import pytest
from dapla_metadata.datasets import Datadoc
from dash import html
from datadoc_model.all_optional import model

from datadoc_editor import constants
from datadoc_editor import enums
from datadoc_editor import state
from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.callbacks.utils import apply_pseudonymization
from datadoc_editor.frontend.callbacks.utils import check_variable_names
from datadoc_editor.frontend.callbacks.utils import find_existing_language_string
from datadoc_editor.frontend.callbacks.utils import map_dropdown_to_pseudo
from datadoc_editor.frontend.callbacks.utils import render_multidropdown_row
from datadoc_editor.frontend.callbacks.utils import render_tabs
from datadoc_editor.frontend.callbacks.utils import save_metadata_and_generate_alerts
from datadoc_editor.frontend.callbacks.utils import update_store_data_with_inputs
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


def test_render_multidropdown_row_simple():
    row = render_multidropdown_row(
        {
            "use_restriction_type": "DELETION_ANONYMIZATION",
            "use_restriction_date": "2025-09-11",
        },
        {"component": "row_test"},
        lambda: [{"label": "Option", "value": "option"}],
        key="",
    )
    assert isinstance(row, html.Div)
    # date and button is inside av Div
    dropdown = row.children[0]

    date_button_div = row.children[1]
    date_input = date_button_div.children[0]
    button = date_button_div.children[1]

    assert dropdown.value == "DELETION_ANONYMIZATION"
    assert dropdown.id == {"component": "row_test", "field": "type"}

    assert date_input.value == "2025-09-11"
    assert date_input.id == {"component": "row_test", "field": "date"}

    assert button.id == {"component": "row_test", "field": "delete"}


def test_save_and_generate_alerts():
    mock_metadata = mock.Mock()

    @dataclass
    class Variable:
        short_name: str  # type: ignore [annotation-unchecked]

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
                    encryption_algorithm="TINK-DAEAD",
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
            PseudonymizationAlgorithmsEnum.CUSTOM,
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


@pytest.mark.parametrize(
    ("type_value", "expected_type", "date_value", "expected_date"),
    [
        (
            enums.UseRestrictionType.DELETION_ANONYMIZATION.value,
            enums.UseRestrictionType.DELETION_ANONYMIZATION.value,
            "2025-01-01",
            "2025-01-01",
        ),
        (None, None, None, None),
    ],
)
def test_valid_type_values_update(type_value, expected_type, date_value, expected_date):
    store_data = [{"use_restriction_type": None, "use_restriction_date": None}]
    type_values = [type_value]
    date_values = [date_value]

    result = update_store_data_with_inputs(store_data, type_values, date_values)

    assert result == [
        {
            "use_restriction_type": expected_type,
            "use_restriction_date": expected_date,
        }
    ]


@pytest.mark.parametrize(
    ("store_data", "type_values", "date_values", "expected"),
    [
        (
            [
                {
                    "use_restriction_type": enums.UseRestrictionType.DELETION_ANONYMIZATION.value,
                    "use_restriction_date": "2025-01-01",
                }
            ],
            [enums.UseRestrictionType.PROCESS_LIMITATIONS.value],
            ["2026-01-01"],
            [
                {
                    "use_restriction_type": enums.UseRestrictionType.PROCESS_LIMITATIONS.value,
                    "use_restriction_date": "2026-01-01",
                }
            ],
        ),
        (
            [
                {
                    "use_restriction_type": enums.UseRestrictionType.DELETION_ANONYMIZATION.value,
                    "use_restriction_date": "2025-01-01",
                },
                {"use_restriction_type": None, "use_restriction_date": None},
            ],
            [
                enums.UseRestrictionType.DELETION_ANONYMIZATION.value,
                enums.UseRestrictionType.PROCESS_LIMITATIONS.value,
            ],
            ["2025-01-01", "2026-01-01"],
            [
                {
                    "use_restriction_type": enums.UseRestrictionType.DELETION_ANONYMIZATION.value,
                    "use_restriction_date": "2025-01-01",
                },
                {
                    "use_restriction_type": enums.UseRestrictionType.PROCESS_LIMITATIONS.value,
                    "use_restriction_date": "2026-01-01",
                },
            ],
        ),
    ],
)
def test_update_store_data_with_inputs(store_data, type_values, date_values, expected):
    assert (
        update_store_data_with_inputs(store_data, type_values, date_values) == expected
    )


def test_find_existing_use_restriction_illegal_input():
    dataset_metadata = model.Dataset()
    with pytest.raises(ValueError, match="is not a valid UseRestrictionType"):
        update_use_restriction_type(
            dataset_metadata, "NOT_A_USE_RESTRICTION", "use_restrictions", 0
        )


@dataclass
class PseudoCase:
    """Test cases Pseudonymization."""

    selected_algorithm: enums.PseudonymizationAlgorithmsEnum | None
    expected_stable_type: str | None
    expected_encryption_algorithm: str | None
    expected_encryption_key_reference: str | None
    expected_algorithm_parameters: list | None
    expected_stable_identifier_version: str | None = None
    saved_pseudonymization: model.Pseudonymization | None = None
    expected_pseudonymization_time: datetime.datetime | None = None
    expected_snapshot_date: str | None = None


@pytest.mark.parametrize(
    "case",
    [
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID,
            expected_stable_type=None,
            expected_encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
            expected_encryption_key_reference=constants.PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.PAPIS_ENCRYPTION_KEY_REFERENCE
                },
                {
                    constants.ENCRYPTION_PARAMETER_STRATEGY: constants.ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID,
            expected_stable_type=constants.PAPIS_STABLE_IDENTIFIER_TYPE,
            expected_encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
            expected_encryption_key_reference=constants.PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.PAPIS_ENCRYPTION_KEY_REFERENCE
                },
                {
                    constants.ENCRYPTION_PARAMETER_STRATEGY: constants.ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
                {
                    constants.ENCRYPTION_PARAMETER_SNAPSHOT_DATE: datetime.datetime.now(
                        datetime.UTC
                    )
                    .date()
                    .isoformat()
                },
            ],
            expected_stable_identifier_version=datetime.datetime.now(datetime.UTC)
            .date()
            .isoformat(),
            expected_snapshot_date=datetime.datetime.now(datetime.UTC)
            .date()
            .isoformat(),
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA,
            expected_stable_type=None,
            expected_encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION,
            expected_encryption_key_reference=constants.DAEAD_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.DAEAD_ENCRYPTION_KEY_REFERENCE
                },
            ],
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.CUSTOM,
            expected_stable_type=None,
            expected_encryption_algorithm=None,
            expected_encryption_key_reference=None,
            expected_algorithm_parameters=None,
        ),
        PseudoCase(
            selected_algorithm=enums.PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID,
            expected_stable_type=None,
            expected_encryption_algorithm=constants.PAPIS_ALGORITHM_ENCRYPTION,
            expected_encryption_key_reference=constants.PAPIS_ENCRYPTION_KEY_REFERENCE,
            expected_algorithm_parameters=[
                {
                    constants.ENCRYPTION_PARAMETER_KEY_ID: constants.PAPIS_ENCRYPTION_KEY_REFERENCE
                },
                {
                    constants.ENCRYPTION_PARAMETER_STRATEGY: constants.ENCRYPTION_PARAMETER_STRATEGY_SKIP
                },
            ],
            saved_pseudonymization=model.Pseudonymization(
                encryption_algorithm=constants.STANDARD_ALGORITM_DAPLA_ENCRYPTION,
                encryption_key_reference=constants.DAEAD_ENCRYPTION_KEY_REFERENCE,
                pseudonymization_time=datetime.datetime(
                    2021, 1, 1, 0, 0, tzinfo=datetime.UTC
                ),
            ),
            expected_pseudonymization_time=None,
        ),
    ],
    ids=[
        "Selected PAPIS without stable ID",
        "Selected PAPIS with stable ID",
        "Selected DAEAD",
        "Selected custom",
        "Reselect: from DAEAD to PAPIS without stable ID",
    ],
)
def test_apply_pseudonymization_based_on_selected_algorithm(case, metadata: Datadoc):
    state.metadata = metadata
    variable = state.metadata.variables_lookup["sykepenger"]
    apply_pseudonymization(
        variable,
        case.selected_algorithm,
    )
    assert variable.pseudonymization is not None
    assert (
        variable.pseudonymization.encryption_algorithm
        == case.expected_encryption_algorithm
    )
    assert variable.pseudonymization.stable_identifier_type == case.expected_stable_type

    assert (
        variable.pseudonymization.encryption_key_reference
        == case.expected_encryption_key_reference
    )
    assert (
        variable.pseudonymization.encryption_algorithm_parameters
        == case.expected_algorithm_parameters
    )
    assert variable.pseudonymization.stable_identifier_type == case.expected_stable_type
    assert (
        variable.pseudonymization.pseudonymization_time
        == case.expected_pseudonymization_time
    )
    assert (
        variable.pseudonymization.stable_identifier_version
        == case.expected_stable_identifier_version
    )
    if case.expected_snapshot_date is not None:
        snapshot_param: dict | None = next(
            (
                p
                for p in variable.pseudonymization.encryption_algorithm_parameters
                if constants.ENCRYPTION_PARAMETER_SNAPSHOT_DATE in p
            ),
            None,
        )
        assert snapshot_param is not None
        assert (
            snapshot_param[constants.ENCRYPTION_PARAMETER_SNAPSHOT_DATE]
            == case.expected_snapshot_date
        )
