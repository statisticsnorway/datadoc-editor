"""Callbacks relating to datasets."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from dapla_metadata.datasets import DaplaDatasetPathInfo
from dapla_metadata.datasets import Datadoc
from dash import no_update

from datadoc_editor import config
from datadoc_editor import state
from datadoc_editor.frontend.callbacks.utils import MetadataInputTypes
from datadoc_editor.frontend.callbacks.utils import MultidropdownInputTypes
from datadoc_editor.frontend.callbacks.utils import find_existing_language_string
from datadoc_editor.frontend.callbacks.utils import get_dataset_path
from datadoc_editor.frontend.callbacks.utils import parse_and_validate_dates
from datadoc_editor.frontend.callbacks.utils import update_use_restriction_date
from datadoc_editor.frontend.callbacks.utils import update_use_restriction_type
from datadoc_editor.frontend.callbacks.variables import (
    set_variables_value_multilanguage_inherit_dataset_values,
)
from datadoc_editor.frontend.callbacks.variables import (
    set_variables_values_inherit_dataset_derived_date_values,
)
from datadoc_editor.frontend.callbacks.variables import (
    set_variables_values_inherit_dataset_values,
)
from datadoc_editor.frontend.components.builders import AlertTypes
from datadoc_editor.frontend.components.builders import build_ssb_alert
from datadoc_editor.frontend.constants import INVALID_DATE_ORDER
from datadoc_editor.frontend.constants import INVALID_VALUE
from datadoc_editor.frontend.fields.display_dataset import DISPLAY_DATASET
from datadoc_editor.frontend.fields.display_dataset import (
    DROPDOWN_DATASET_METADATA_IDENTIFIERS,
)
from datadoc_editor.frontend.fields.display_dataset import (
    MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS,
)
from datadoc_editor.frontend.fields.display_dataset import DatasetIdentifiers
from datadoc_editor.utils import METADATA_DOCUMENT_FILE_SUFFIX

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc
    from dapla_metadata.datasets import model
    from dapla_metadata.datasets._merge import DatasetConsistencyStatus

logger = logging.getLogger(__name__)


def open_file(file_path: str | None = None) -> Datadoc:
    """Load the given dataset into a DataDocMetadata instance."""
    if file_path and file_path.endswith(METADATA_DOCUMENT_FILE_SUFFIX):
        logger.info("Opening existing metadata document %s", file_path)
        return Datadoc(
            metadata_document_path=file_path.strip(),
            statistic_subject_mapping=state.statistic_subject_mapping,
        )

    dataset = file_path or get_dataset_path()
    if dataset:
        logger.info("Opening dataset %s", dataset)
    return Datadoc(
        dataset_path=str(dataset).strip() if dataset else None,
        statistic_subject_mapping=state.statistic_subject_mapping,
    )


def open_dataset_handling(
    n_clicks: int,
    file_path: str,
    dataset_opened_counter: int,
) -> tuple[dbc.Alert, int | Any]:
    """Handle errors and other logic around opening a dataset file."""
    if file_path:
        file_path = file_path.strip()
    try:
        state.metadata = open_file(file_path)
        set_variables_values_inherit_dataset_derived_date_values()
    except FileNotFoundError:
        logger.exception("File %s not found", str(file_path))
        try:
            metadata_file_path = str(
                Path(file_path).with_name(
                    Path(file_path).stem + METADATA_DOCUMENT_FILE_SUFFIX
                )
            )
            open_file(metadata_file_path)
            logger.info("Metadata-document found: %s", metadata_file_path)
            return (
                build_ssb_alert(
                    AlertTypes.WARNING,
                    "Datasettet finnes ikke, men metadata eksisterer",
                    message=f"{metadata_file_path}. Har datasettet endret navn eller blitt slettet?",
                ),
                no_update,
            )
        except FileNotFoundError:
            logger.exception("Metadata-document %s not found", str(metadata_file_path))
            return (
                build_ssb_alert(
                    AlertTypes.ERROR,
                    "Kunne ikke åpne datasettet",
                    message=f"Datasettet '{file_path}' finnes ikke.",
                ),
                no_update,
            )
    except Exception:
        logger.exception("Could not open %s", str(file_path))
        return (
            build_ssb_alert(
                AlertTypes.ERROR,
                "Kunne ikke åpne datasettet",
                message=f"Kunne ikke åpne datasettet '{file_path}'.",
            ),
            no_update,
        )
    dataset_opened_counter += 1
    if n_clicks and n_clicks > 0:
        dapla_dataset_path_info = DaplaDatasetPathInfo(file_path)
        if not dapla_dataset_path_info.path_complies_with_naming_standard():
            return (
                build_ssb_alert(
                    AlertTypes.WARNING,
                    "Filen følger ikke navnestandard",
                    message="Vennligst se mer informasjon her:",
                    link=config.get_dapla_manual_naming_standard_url(),
                ),
                dataset_opened_counter,
            )
        status: list[DatasetConsistencyStatus] = (
            state.metadata.dataset_consistency_status
        )
        failed_items = [item.message for item in status or [] if not item.success]
        if failed_items:
            return (
                build_ssb_alert(
                    AlertTypes.WARNING,
                    "Det er inkonsistens mellom data og metadata for:",
                    alert_list=list(failed_items),
                ),
                dataset_opened_counter,
            )
    return (
        build_ssb_alert(
            AlertTypes.SUCCESS,
            "Åpnet datasett",
        ),
        dataset_opened_counter,
    )


def process_keyword(value: str) -> list[str]:
    """Convert a comma separated string to a list of strings.

    e.g. 'a,b ,c' -> ['a', 'b', 'c']
    """
    return [item.strip() for item in value.split(",")]


def process_special_cases(
    value: MetadataInputTypes | model.LanguageStringType,
    metadata_identifier: str,
    language: str | None = None,
) -> MetadataInputTypes | model.LanguageStringType:
    """Pre-process metadata where needed.

    Some types of metadata need processing before being saved
    to the model. Handle these cases here, other values are
    returned unchanged.
    """
    updated_value: MetadataInputTypes | model.LanguageStringType
    if metadata_identifier == DatasetIdentifiers.KEYWORD.value and isinstance(
        value,
        str,
    ):
        updated_value = process_keyword(value)
    elif metadata_identifier == DatasetIdentifiers.VERSION.value:
        updated_value = str(value)
    elif metadata_identifier in MULTIPLE_LANGUAGE_DATASET_IDENTIFIERS and isinstance(
        value,
        str,
    ):
        if language is not None:
            updated_value = find_existing_language_string(
                state.metadata.dataset,
                value,
                metadata_identifier,
                language,
            )
            set_variables_value_multilanguage_inherit_dataset_values(
                value,
                metadata_identifier,
                language,
            )
    elif metadata_identifier in DROPDOWN_DATASET_METADATA_IDENTIFIERS and value == "":
        updated_value = None
    else:
        updated_value = value

    # Other values get returned unchanged
    return updated_value


def accept_dataset_metadata_input(
    value: MetadataInputTypes | model.LanguageStringType,
    metadata_identifier: str,
    language: str | None = None,
) -> tuple[bool, str]:
    """Handle user inputs of dataset metadata values."""
    logger.debug(
        "Received updated value = %s for metadata_identifier = %s",
        value,
        metadata_identifier,
    )
    try:
        value = process_special_cases(value, metadata_identifier, language)
        # Update the value in the model
        setattr(
            state.metadata.dataset,
            metadata_identifier,
            value,
        )
        set_variables_values_inherit_dataset_values(value, metadata_identifier)
    except ValueError:
        show_error = True
        error_explanation = INVALID_VALUE
        logger.exception("Error while reading in value for %s", metadata_identifier)
    else:
        show_error = False
        error_explanation = ""
        logger.info(
            "Updated dataset %s with value %s",
            metadata_identifier,
            value,
        )

    return show_error, error_explanation


def accept_dataset_multidropdown_input(
    updated_value: MultidropdownInputTypes,
    metadata_identifier: str,
    field: str,
    index: int,
) -> tuple[bool, str]:
    """Handle user inputs of dataset multidropdown values."""
    logger.debug(
        "Received updated value = %s for metadata_identifier = %s",
        updated_value,
        metadata_identifier,
    )
    try:
        if field == "type":
            updated_multidropdown_list = update_use_restriction_type(
                state.metadata.dataset, updated_value, metadata_identifier, index
            )
        elif field == "date":
            updated_multidropdown_list = update_use_restriction_date(
                state.metadata.dataset, updated_value, metadata_identifier, index
            )
        setattr(
            state.metadata.dataset,
            metadata_identifier,
            updated_multidropdown_list,
        )
    except ValueError:
        show_error = True
        error_explanation = INVALID_VALUE
        logger.exception("Error while reading in value for %s", metadata_identifier)
    else:
        show_error = False
        error_explanation = ""
        logger.info(
            "Updated dataset %s with value %s",
            metadata_identifier,
            updated_multidropdown_list,
        )

    return show_error, error_explanation


def remove_dataset_multidropdown_input(metadata_identifier: str, index: int) -> None:
    """Remove a row from the multidropdown component."""
    logger.debug(
        "Removing row %d for metadata_identifier = %s", index, metadata_identifier
    )

    restrictions = state.metadata.dataset.use_restrictions
    if restrictions is None:
        logger.error("use_restrictions is None for %s", metadata_identifier)
        return

    if 0 <= index < len(restrictions):
        restrictions.pop(index)
        logger.info("Removed row %d from dataset %s", index, metadata_identifier)
    else:
        logger.warning("Invalid index %d for %s", index, metadata_identifier)


def accept_dataset_metadata_date_input(
    dataset_identifier: DatasetIdentifiers,
    contains_data_from: str | None,
    contains_data_until: str | None,
) -> tuple[bool, str, bool, str]:
    """Validate and save date range inputs."""
    message = ""
    try:
        (
            parsed_contains_data_from,
            parsed_contains_data_until,
        ) = parse_and_validate_dates(
            str(contains_data_from),
            str(contains_data_until),
        )
        if dataset_identifier == DatasetIdentifiers.CONTAINS_DATA_FROM:
            set_variables_values_inherit_dataset_values(
                contains_data_from,
                dataset_identifier,
            )
        if dataset_identifier == DatasetIdentifiers.CONTAINS_DATA_UNTIL:
            set_variables_values_inherit_dataset_values(
                contains_data_until,
                dataset_identifier,
            )
        if parsed_contains_data_from:
            state.metadata.dataset.contains_data_from = parsed_contains_data_from
        if parsed_contains_data_until:
            state.metadata.dataset.contains_data_until = parsed_contains_data_until
    except ValueError as e:
        logger.exception(
            "Validation failed for %s, %s, %s: %s, %s",
            dataset_identifier,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )
        message = str(e)
    else:
        logger.debug(
            "Successfully updated %s, %s, %s: %s, %s",
            dataset_identifier,
            "contains_data_from",
            contains_data_from,
            "contains_data_until",
            contains_data_until,
        )

    no_error = (False, "")
    if not message:
        # No error to display.
        return no_error + no_error

    error = (
        True,
        INVALID_DATE_ORDER.format(
            contains_data_from_display_name=DISPLAY_DATASET[
                DatasetIdentifiers.CONTAINS_DATA_FROM
            ].display_name,
            contains_data_until_display_name=DISPLAY_DATASET[
                DatasetIdentifiers.CONTAINS_DATA_UNTIL
            ].display_name,
        ),
    )
    return (
        error + no_error
        if dataset_identifier == DatasetIdentifiers.CONTAINS_DATA_FROM
        else no_error + error
    )
