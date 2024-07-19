from __future__ import annotations

import datetime  # noqa: TCH003 import is needed in xdoctest
import pathlib
import uuid

from cloudpathlib import CloudPath
from cloudpathlib import GSClient
from cloudpathlib import GSPath
from dapla import AuthClient
from datadoc_model import model

from datadoc.backend.constants import OBLIGATORY_DATASET_METADATA_IDENTIFIERS
from datadoc.backend.constants import OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS
from datadoc.enums import Assessment
from datadoc.enums import DataSetState


def normalize_path(path: str) -> pathlib.Path | CloudPath:
    """Obtain a pathlib compatible Path regardless of whether the file is on a filesystem or in GCS.

    Args:
        path (str):
            Path on a filesystem or in cloud storage

    Returns:
        pathlib.Path | CloudPath:
            Pathlib compatible object
    """
    if path.startswith(GSPath.cloud_prefix):
        client = GSClient(credentials=AuthClient.fetch_google_credentials())
        return GSPath(path, client=client)
    return pathlib.Path(path)


def calculate_percentage(completed: int, total: int) -> int:
    """Calculate percentage as a rounded integer."""
    return round((completed / total) * 100)


def derive_assessment_from_state(state: DataSetState) -> Assessment:
    """Derive assessment from dataset state.

    Args:
        state (DataSetState):
            The state of the dataset.

    Returns:
        Assessment:
            The derived assessment of the dataset.
    """
    match (state):
        case (
            DataSetState.INPUT_DATA
            | DataSetState.PROCESSED_DATA
            | DataSetState.STATISTICS
        ):
            return Assessment.PROTECTED
        case DataSetState.OUTPUT_DATA:
            return Assessment.OPEN
        case DataSetState.SOURCE_DATA:
            return Assessment.SENSITIVE


def set_default_values_variables(variables: list) -> None:
    """Set default values on variables.

    For variable fields 'id' and 'is personal data'

    Example:
        >>> variables = [model.Variable(short_name="pers",id=None, is_personal_data = None), model.Variable(short_name="fnr",id='9662875c-c245-41de-b667-12ad2091a1ee', is_personal_data='PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA')]
        >>> set_default_values_variables(variables)
        >>> isinstance(variables[0].id, uuid.UUID)
        True

        >>> variables[1].is_personal_data == 'PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA'
        True

        >>> variables[0].is_personal_data == 'NOT_PERSONAL_DATA'
        True

    Args:
        variables (list):
            A list of variables
    """
    for v in variables:
        if v.id is None:
            v.id = uuid.uuid4()
        if v.is_personal_data is None:
            v.is_personal_data = model.IsPersonalData.NOT_PERSONAL_DATA


def set_default_values_dataset(dataset: model.Dataset) -> None:
    """Set default values on dataset.

    For dataset fields 'id' and 'contains personal data'

    Example:
        >>> dataset = model.Dataset(id=None, contains_personal_data=None)
        >>> set_default_values_dataset(dataset)
        >>> dataset.id is not None
        True

        >>> dataset.contains_personal_data == False
        True

    Args:
        dataset (model.Dataset):
            The model for dataset metadata
    """
    if not dataset.id:
        dataset.id = uuid.uuid4()
    if dataset.contains_personal_data is None:
        dataset.contains_personal_data = False


def set_variables_inherit_from_dataset(
    dataset: model.Dataset,
    variables: list,
) -> None:
    """Set dataset values on variables.

    For variable fields:
        'data source'
        'temporality type',
        'contains data from',
        'contains data until',

    If a variable field from list has no value it will inherit from dataset value.

    Example:
        >>> dataset = model.Dataset(short_name='person_data_v1',data_source='01',temporality_type='STATUS',id='9662875c-c245-41de-b667-12ad2091a1ee',contains_data_from="2010-09-05",contains_data_until="2022-09-05")
        >>> variables = [model.Variable(short_name="pers",data_source =None,temporality_type = None, contains_data_from = None,contains_data_until = None)]
        >>> set_variables_inherit_from_dataset(dataset, variables)
        >>> variables[0].data_source == dataset.data_source
        True

        >>> variables[0].temporality_type is None
        False

        >>> variables[0].contains_data_from == dataset.contains_data_from
        True

        >>> variables[0].contains_data_until == dataset.contains_data_until
        True

    Args:
        dataset (model.Dataset):
            current dataset
        variables (list):
            current list of variables
    """
    for v in variables:
        v.contains_data_from = v.contains_data_from or dataset.contains_data_from
        v.contains_data_until = v.contains_data_until or dataset.contains_data_until
        v.temporality_type = v.temporality_type or dataset.temporality_type
        v.data_source = v.data_source or dataset.data_source


def incorrect_date_order(
    date_from: datetime.date | None,
    date_until: datetime.date | None,
) -> bool:
    """Evaluate date order of two dates.

    If 'date until' is before 'date from' it is incorrect date order.

    Example:
        >>> incorrect_date_order(datetime.date(1980, 1, 1), datetime.date(1967, 1, 1))
        True

        >>> incorrect_date_order(datetime.date(1967, 1, 1), datetime.date(1980, 1, 1))
        False

    Args:
        date_from (datetime.date):
            start date of time period
        date_until (datetime.date):
            end date of time period

    Returns:
        True if it is incorrect date order.
    """
    return date_from is not None and date_until is not None and date_until < date_from


def num_obligatory_dataset_fields_completed(dataset: model.Dataset) -> int:
    """Return the number of obligatory dataset fields with value."""
    return len(
        [
            k
            for k, v in dataset.model_dump().items()
            if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is not None
        ],
    )


def num_obligatory_variables_fields_completed(variables: list) -> int:
    """Return the number of obligatory variable fields for one variable with value."""
    num_variables = 0
    for variable in variables:
        num_variables = len(
            [
                k
                for k, v in variable.model_dump().items()
                if k in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS and v is not None
            ],
        )
    return num_variables


def get_missing_obligatory_dataset_fields(dataset: model.Dataset) -> list:
    """Get all obligatory dataset fields with no value.

    Args:
        dataset (model.Dataset):
            The dataset examined.

    Returns:
        List of obligatory dataset fields who are missing value.
    """
    return [
        k
        for k, v in dataset.model_dump().items()
        if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is None
    ]


def get_missing_obligatory_variables_fields(variables) -> list[dict]:  # noqa: ANN001
    """Get all obligatory variable fields for with no value for all variables.

    Each dict has variable shortname as key and a list of missing fields.

    Args:
        variables (list):
            List of variables in.

    Returns:
        List of dicts with variables obligatory variable fields who are missing value.
    """
    return [
        {
            variable.short_name: [
                k
                for k, v in variable.model_dump().items()
                if k in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS and v is None
            ],
        }
        for variable in variables
    ]
