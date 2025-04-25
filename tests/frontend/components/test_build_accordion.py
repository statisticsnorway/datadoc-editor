"""Test function build_ssb_accordion."""

import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]

from datadoc_editor.frontend.components.builders import build_ssb_accordion
from datadoc_editor.frontend.fields.display_variables import (
    OBLIGATORY_VARIABLES_METADATA,
)
from datadoc_editor.frontend.fields.display_variables import OPTIONAL_VARIABLES_METADATA

ACCORDION_TYPE = "variables-accordion"


@pytest.mark.parametrize(
    ("name", "dict_id", "field_list"),
    [
        (
            "pers_id",
            {"type": ACCORDION_TYPE, "id": "pers_id"},
            [],
        ),
        (
            "sykepenger",
            {"type": ACCORDION_TYPE, "id": "sykepenger"},
            OPTIONAL_VARIABLES_METADATA,
        ),
        (
            "ber_bruttoformue",
            {"type": ACCORDION_TYPE, "id": "ber_bruttoformue"},
            OBLIGATORY_VARIABLES_METADATA,
        ),
        (
            "hoveddiagnose",
            {"type": ACCORDION_TYPE, "id": "hoveddiagnose"},
            [],
        ),
        (
            "",
            {"type": ACCORDION_TYPE, "id": ""},
            OBLIGATORY_VARIABLES_METADATA,
        ),
    ],
)
def test_build_ssb_accordion(name, dict_id, field_list):
    accordion = build_ssb_accordion(name, dict_id, name, field_list)
    assert accordion.id["type"] == ACCORDION_TYPE
    assert accordion.id["id"] == accordion.header
    assert isinstance(accordion, ssb.Accordion)
