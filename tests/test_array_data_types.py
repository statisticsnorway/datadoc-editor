"""Tests for array data types with known inner types."""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from dapla_metadata.datasets import Datadoc

from datadoc_editor.enums import DataType
from datadoc_editor.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers

ARRAY_TYPES_PARQUET = (
    Path(__file__).parent / "resources" / "datasets" / "array_types.parquet"
)

EXPECTED_ARRAY_TYPES = {
    "array_string": "ARRAY[STRING]",
    "array_integer": "ARRAY[INTEGER]",
    "array_datetime": "ARRAY[DATETIME]",
    "array_boolean": "ARRAY[BOOLEAN]",
    "array_float": "ARRAY[FLOAT]",
}


def test_array_data_type_enum_values():
    assert {
        data_type.name: data_type.value
        for data_type in DataType
        if data_type.name.startswith("ARRAY_")
    } == {
        "ARRAY_STRING_": "ARRAY[STRING]",
        "ARRAY_INTEGER_": "ARRAY[INTEGER]",
        "ARRAY_DATETIME_": "ARRAY[DATETIME]",
        "ARRAY_BOOLEAN_": "ARRAY[BOOLEAN]",
        "ARRAY_FLOAT_": "ARRAY[FLOAT]",
    }


def test_array_types_parquet_contains_all_supported_inner_types():
    schema = pq.read_schema(ARRAY_TYPES_PARQUET)

    assert schema == pa.schema(
        [
            pa.field("array_string", pa.list_(pa.string())),
            pa.field("array_integer", pa.list_(pa.int64())),
            pa.field("array_datetime", pa.list_(pa.timestamp("us"))),
            pa.field("array_boolean", pa.list_(pa.bool_())),
            pa.field("array_float", pa.list_(pa.float64())),
        ]
    )


@pytest.mark.usefixtures("_mock_user_info")
def test_array_inner_types_are_opened_and_displayed(
    subject_mapping_fake_statistical_structure,
):
    metadata = Datadoc(
        dataset_path=ARRAY_TYPES_PARQUET,
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
        errors_as_warnings=True,
    )

    assert {
        variable.short_name: variable.data_type for variable in metadata.variables
    } == EXPECTED_ARRAY_TYPES

    data_type_field = DISPLAY_VARIABLES[VariableIdentifiers.DATA_TYPE]
    assert {
        variable.short_name: data_type_field.render(
            component_id={
                "type": "variables-metadata-input",
                "variable_short_name": variable.short_name,
                "id": "data_type",
            },
            metadata=variable,
        ).value
        for variable in metadata.variables
    } == EXPECTED_ARRAY_TYPES
