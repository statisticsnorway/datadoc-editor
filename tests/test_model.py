"""Verify that we are in sync with the Model."""

from dapla_metadata.datasets import model

from datadoc_editor.frontend.fields.display_dataset import DISPLAY_DATASET
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc_editor.frontend.fields.display_variables import DISPLAY_VARIABLES
from datadoc_editor.frontend.fields.display_variables import VariableIdentifiers


def test_dataset_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    datadoc_values = sorted([i.value for i in DatasetIdentifiers])
    model_values = sorted(model.Dataset().model_dump().keys())

    # TODO @Jorgen-5: Fields that are currently not supported by datadoc # noqa: TD003
    model_values.remove("custom_type")

    assert datadoc_values == model_values
    assert sorted(DatasetIdentifiers) == sorted(DISPLAY_DATASET.keys())


def test_variables_metadata_definition_parity():
    """The metadata fields are currently defined in multiple places for technical reasons. We want these to always be exactly identical."""
    datadoc_values = sorted([i.value for i in VariableIdentifiers])
    model_values = sorted(model.Variable().model_dump().keys())

    # TODO @Jorgen-5: Fields that are currently not supported by datadoc # noqa: TD003
    model_values.remove("custom_type")
    model_values.remove("special_value")
    model_values.remove("pseudonymization")

    assert datadoc_values == model_values

    assert sorted(VariableIdentifiers) == sorted(DISPLAY_VARIABLES.keys())
