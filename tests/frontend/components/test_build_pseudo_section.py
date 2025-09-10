from dash import html
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dapla_metadata.datasets import model

from datadoc_editor.enums import PseudonymizationAlgorithmsEnum
from datadoc_editor.frontend.components.builders import (
    build_variables_pseudonymization_section,
)
from datadoc_editor.frontend.fields.display_base import MetadataInputField
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_DEAD_METADATA,
)
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_METADATA,
)
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_PAPIS_WITH_STABLE_ID_METADATA,
)
from datadoc_editor.frontend.fields.display_pseudo_variables import (
    PSEUDONYMIZATION_PAPIS_WITHOUT_STABLE_ID_METADATA,
)

PSEDUO_VARIABLES_METADATA = PSEUDONYMIZATION_METADATA

SELECTED_ALGORITHMS = [
    PSEUDONYMIZATION_PAPIS_WITH_STABLE_ID_METADATA,
    PSEUDONYMIZATION_PAPIS_WITHOUT_STABLE_ID_METADATA,
    PSEUDONYMIZATION_DEAD_METADATA,
]

PSEUDO_INPUT_FIELD_SECTION = [
    (
        PSEUDONYMIZATION_PAPIS_WITH_STABLE_ID_METADATA,
        model.Variable(short_name="hoveddiagnose"),
    ),
]

@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("selected_algorithm", "variable"),
    PSEUDO_INPUT_FIELD_SECTION,
)
def test_build_pseudo_input_section(
    selected_algorithm,
    variable,
):
    variable.pseudonymization = model.Pseudonymization()
    input_section = build_variables_pseudonymization_section(
        "Pseudonymisert", variable, selected_algorithm
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

@pytest.mark.usefixtures("_code_list_fake_classifications")
@pytest.mark.parametrize(
    ("selected_algorithm", "variable", "num_pseudo_fields"),
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
    ],
    ids=["papis_with_stable_id"]
)
def test_build_pseudo_input_section_2(
    selected_algorithm,
    variable,
    num_pseudo_fields
):
    #variable.pseudonymization = model.Pseudonymization()
    section = build_variables_pseudonymization_section(
        "Pseudonymisert", variable, selected_algorithm
    )
    assert section is not None
    
    assert isinstance(section, html.Section)
    assert section.id["title"] == "Pseudonymisert"

    children = [c for c in section.children if isinstance(c, ssb.Dropdown)]
    dropdown = children[0]
    assert dropdown.value == selected_algorithm

#    assert all(item for item in [e.values for e in dropdown.items] for e in PseudonymizationAlgorithmsEnum)
#    
#    container_divs = [
#        c for c in section.children
#        if isinstance(c, html.Div) and c.id.get("variable") == variable.short_name
#    ]
#    assert len(container_divs) == 1
#    container_div = container_divs[0]
#    
#    container_divs = [
#        c for c in section.children
#        if isinstance(c, html.Div) and c.id.get("variable") == variable.short_name
#    ]
#    assert len(container_divs) == 1
#    container_div = container_divs[0]
#
#
#    elements_of_input = [
#        element for element in input_section.children if isinstance(element, ssb.Input)
#    ]
#
#    variable_identifier_input = [
#        element
#        for element in PSEUDONYMIZATION_METADATA
#        if isinstance(element, MetadataInputField)
#    ]
#    assert all(isinstance(field, ssb.Input) for field in elements_of_input)
#    assert all(item.debounce is True for item in elements_of_input)
#    assert all(
#        item1.label == item2.display_name
#        for item1, item2 in zip(
#            elements_of_input,
#            variable_identifier_input,
#            strict=False,
#        )
#    )
#