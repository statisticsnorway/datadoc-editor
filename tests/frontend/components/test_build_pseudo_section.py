import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dapla_metadata.datasets import model
from dash import html

from datadoc_editor.frontend.callbacks.utils import map_dropdown_to_pseudo
from datadoc_editor.frontend.callbacks.utils import (
    map_selected_algorithm_to_pseudo_fields,
)
from datadoc_editor.frontend.components.builders import build_pseudo_field_section
from datadoc_editor.frontend.components.builders import (
    build_variables_pseudonymization_section,
)


@pytest.mark.parametrize(
    ("expected_algorithm", "variable", "num_editable_fields"),
    [
        (
            "PAPIS_ALGORITHM_WITH_STABLE_ID",
            model.Variable(
                short_name="helse",
                pseudonymization=model.Pseudonymization(
                    stable_identifier_type="FREG_SNR", encryption_algorithm="TINK-FPE"
                ),
            ),
            2,
        ),
        (
            "PAPIS_ALGORITHM_WITHOUT_STABLE_ID",
            model.Variable(
                short_name="helse",
                pseudonymization=model.Pseudonymization(
                    encryption_algorithm="TINK-FPE"
                ),
            ),
            1,
        ),
        (
            "STANDARD_ALGORITM_DAPLA",
            model.Variable(
                short_name="helse",
                pseudonymization=model.Pseudonymization(
                    encryption_algorithm="TINK-DAED"
                ),
            ),
            1,
        ),
        (
            "CUSTOM",
            model.Variable(
                short_name="helse",
                pseudonymization=model.Pseudonymization(encryption_algorithm="LOK"),
            ),
            5,
        ),
        (
            "",
            model.Variable(
                short_name="helse",
                pseudonymization=None,
            ),
            0,
        ),
        (
            "",
            model.Variable(
                short_name="helse",
                pseudonymization=model.Pseudonymization(
                    stable_identifier_type="FREG_SNR"
                ),
            ),
            0,
        ),
    ],
    ids=[
        "papis_with_stable_id",
        "papis_without_stable_id",
        "standard_dapla",
        "custom_algorithm",
        "no_pseudonymization",
        "not_required_encryption_algorithm",
    ],
)
def test_build_pseudo_input_section(expected_algorithm, variable, num_editable_fields):
    pseudo_section = build_variables_pseudonymization_section(
        "Pseudonymisert", variable, map_dropdown_to_pseudo(variable)
    )
    assert pseudo_section is not None
    assert isinstance(pseudo_section, html.Section)
    assert pseudo_section.id["title"] == "Pseudonymisert"

    children = [c for c in pseudo_section.children if isinstance(c, ssb.Dropdown)]
    dropdown = children[0]
    assert dropdown.value == expected_algorithm

    container_divs = [
        c
        for c in pseudo_section.children
        if isinstance(c, html.Div) and c.id.get("variable") == variable.short_name
    ]
    assert len(container_divs) == 1

    pseudo_metadata_list = map_selected_algorithm_to_pseudo_fields(expected_algorithm)
    input_section = build_pseudo_field_section(
        pseudo_metadata_list,
        "left",
        variable,
        variable.pseudonymization,
    )
    editable_fields = input_section.children
    assert len(editable_fields) == num_editable_fields
    if editable_fields:
        assert all(isinstance(field, ssb.Input) for field in editable_fields)
        assert all(
            item1.label == item2.display_name
            for item1, item2 in zip(
                editable_fields,
                pseudo_metadata_list,
                strict=False,
            )
        )
