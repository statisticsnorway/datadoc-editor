from enum import Enum

from datadoc.frontend.fields.display_base import FieldTypes
from datadoc.frontend.fields.display_base import MetadataInputField


class PseudonomizationItifiers(str, Enum):
    """Pseudo fileds."""

    SHORT_NAME = "short_name"
    DATA_ELEMENT_PATH = "data_element_path"
    STABLE_IDENTIFIER_TYPE = "stable_identifier_type"
    ENCRYPTION_ALGORITHM = "encryption_algorithm"
    ENCRYPTION_KEY_REFERENCE = "encryption_key_reference"
    ENCRYPTION_ALGORITHM_PARAMETERS = "encryption_algorithm_parameters"
    SOURCE_VARIABLE = "source_variable"
    SOURCE_DISPLAY_DATATYPE = "source_variable_datatype"


PSEUDO_FILEDS: dict[
    PseudonomizationItifiers,
    FieldTypes,
] = {
    PseudonomizationItifiers.SHORT_NAME: MetadataInputField(
        identifier=PseudonomizationItifiers.SHORT_NAME.value,
        display_name="Shortname",
        description="",
        obligatory=True,
        editable=False,
    ),
    PseudonomizationItifiers.DATA_ELEMENT_PATH: MetadataInputField(
        identifier=PseudonomizationItifiers.DATA_ELEMENT_PATH.value,
        display_name="Data element path",
        description="",
        obligatory=True,
    ),
    PseudonomizationItifiers.STABLE_IDENTIFIER_TYPE: MetadataInputField(
        identifier=PseudonomizationItifiers.STABLE_IDENTIFIER_TYPE.value,
        display_name="Identifier",
        description="",
        obligatory=True,
    ),
    PseudonomizationItifiers.ENCRYPTION_ALGORITHM: MetadataInputField(
        identifier=PseudonomizationItifiers.ENCRYPTION_ALGORITHM.value,
        display_name="Identifier",
        description="",
        obligatory=True,
    ),
    PseudonomizationItifiers.ENCRYPTION_KEY_REFERENCE: MetadataInputField(
        identifier=PseudonomizationItifiers.ENCRYPTION_KEY_REFERENCE.value,
        display_name="Identifier",
        description="",
        obligatory=True,
    ),
    PseudonomizationItifiers.ENCRYPTION_ALGORITHM_PARAMETERS: MetadataInputField(
        identifier=PseudonomizationItifiers.ENCRYPTION_ALGORITHM_PARAMETERS.value,
        display_name="Encryption algorithm paramaters",
        description="",
        obligatory=True,
    ),
    PseudonomizationItifiers.SOURCE_VARIABLE: MetadataInputField(
        identifier=PseudonomizationItifiers.SOURCE_VARIABLE.value,
        display_name="Identifier",
        description="",
        obligatory=True,
    ),
    PseudonomizationItifiers.SOURCE_DISPLAY_DATATYPE: MetadataInputField(
        identifier=PseudonomizationItifiers.SOURCE_DISPLAY_DATATYPE.value,
        display_name="Identifier",
        description="",
        obligatory=True,
    ),
}

PSEUDONYMIZATION_METADATA = list(PSEUDO_FILEDS.values())
