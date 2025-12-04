import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model.all_optional import model

from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.callbacks.utils import map_dropdown_to_pseudo
from datadoc_editor.frontend.callbacks.utils import (
    map_selected_algorithm_to_pseudo_fields,
)
from datadoc_editor.frontend.components.builders import build_pseudo_field_section
from datadoc_editor.frontend.components.builders import (
    build_variables_pseudonymization_section,
)
from datadoc_editor.frontend.constants import PSEUDONYMIZATION

TEST_VARIABLES = [
    (
        PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID,
        model.Variable(
            short_name="helse",
            pseudonymization=model.Pseudonymization(
                stable_identifier_type="FREG_SNR", encryption_algorithm="TINK-FPE"
            ),
        ),
        2,
    ),
    (
        PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITH_STABLE_ID,
        model.Variable(
            short_name="helse",
            pseudonymization=model.Pseudonymization(
                stable_identifier_type="FREG_SNR",
                encryption_algorithm="TINK-FPE",
                stable_identifier_version="2025-01-01",
            ),
        ),
        2,
    ),
    (
        PseudonymizationAlgorithmsEnum.PAPIS_ALGORITHM_WITHOUT_STABLE_ID,
        model.Variable(
            short_name="helse",
            pseudonymization=model.Pseudonymization(encryption_algorithm="TINK-FPE"),
        ),
        1,
    ),
    (
        PseudonymizationAlgorithmsEnum.STANDARD_ALGORITM_DAPLA,
        model.Variable(
            short_name="helse",
            pseudonymization=model.Pseudonymization(encryption_algorithm="TINK-DAEAD"),
        ),
        1,
    ),
    (
        PseudonymizationAlgorithmsEnum.CUSTOM,
        model.Variable(
            short_name="helse",
            pseudonymization=model.Pseudonymization(encryption_algorithm="LOK"),
        ),
        5,
    ),
    (
        None,
        model.Variable(
            short_name="helse",
            pseudonymization=None,
        ),
        0,
    ),
    (
        PseudonymizationAlgorithmsEnum.CUSTOM,
        model.Variable(
            short_name="helse",
            pseudonymization=model.Pseudonymization(stable_identifier_type="FREG_SNR"),
        ),
        5,
    ),
]

TEST_IDS = [
    "papis_with_stable_id",
    "papis_with_stable_id and version",
    "papis_without_stable_id",
    "standard_dapla",
    "custom_algorithm",
    "no_pseudonymization",
    "not_required_encryption_algorithm",
]


@pytest.mark.parametrize(
    ("expected_algorithm", "variable", "num_editable_fields"),
    TEST_VARIABLES,
    ids=TEST_IDS,
)
def test_build_variables_pseudonymization_section(
    expected_algorithm,
    variable,
    num_editable_fields,  # noqa: ARG001
):
    pseudo_section = build_variables_pseudonymization_section(
        PSEUDONYMIZATION, variable, map_dropdown_to_pseudo(variable)
    )

    assert isinstance(pseudo_section, html.Section)
    assert pseudo_section.id["title"] == PSEUDONYMIZATION

    dropdowns = [c for c in pseudo_section.children if isinstance(c, ssb.Dropdown)]
    assert len(dropdowns) == 1
    dropdown = dropdowns[0]
    assert (dropdown.value or None) == (
        expected_algorithm.value if expected_algorithm else None
    )

    container_divs = [
        c
        for c in pseudo_section.children
        if isinstance(c, html.Div) and c.id.get("variable") == variable.short_name
    ]
    assert len(container_divs) == 1


@pytest.mark.parametrize(
    ("expected_algorithm", "variable", "num_editable_fields"),
    TEST_VARIABLES,
    ids=TEST_IDS,
)
def test_build_pseudonymization_field_section(
    expected_algorithm, variable, num_editable_fields
):
    pseudo_metadata_list = map_selected_algorithm_to_pseudo_fields(expected_algorithm)

    pseudo_edit_section = build_pseudo_field_section(
        pseudo_metadata_list,
        "left",
        variable,
        variable.pseudonymization,
    )
    editable_fields = pseudo_edit_section.children

    assert len(editable_fields) == num_editable_fields, (
        f"Expected {num_editable_fields} editable fields, got {len(editable_fields)}"
    )

    assert all(isinstance(field, ssb.Input) for field in editable_fields), (
        "All editable fields should be ssb.Input components"
    )

    assert all(
        field.label == meta.display_name
        for field, meta in zip(editable_fields, pseudo_metadata_list, strict=True)
    ), "Editable field labels do not match pseudo metadata display names"
