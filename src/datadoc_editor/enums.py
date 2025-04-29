"""Enumerations used in Datadoc."""

from __future__ import annotations

from enum import Enum

from dapla_metadata.datasets import enums
from dapla_metadata.datasets import model


class LanguageStringsEnum(Enum):
    """Enum class for storing LanguageStringType objects."""

    def __init__(
        self,
        language_strings: model.LanguageStringType,
    ) -> None:
        """Store the LanguageStringType object for displaying enum values in multiple languages.

        We don't particularly care what the value of the enum is,
        but when serialised it's convenient and readable to use the
        name of the enum, so we set the value to be the name.
        """
        self._value_ = self.name
        self.language_strings = language_strings

    def get_value_for_language(
        self,
        language: enums.SupportedLanguages,
    ) -> str | None:
        """Retrieve the string for the relevant language."""
        if self.language_strings.root is not None:
            for item in self.language_strings.root:
                if item.languageCode == language:
                    return item.languageText
        return None


class Assessment(LanguageStringsEnum):
    """Sensitivity of data."""

    SENSITIVE = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.Assessment.SENSITIVE.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="SENSITIV"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="SENSITIV"),
        ],
    )
    PROTECTED = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.Assessment.PROTECTED.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="SKJERMET"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="SKJERMET"),
        ],
    )
    OPEN = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.Assessment.OPEN.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="ÅPEN"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="ÅPEN"),
        ],
    )


class DataSetStatus(LanguageStringsEnum):
    """Lifecycle status of a dataset."""

    DRAFT = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.DRAFT.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="UTKAST"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="UTKAST"),
        ],
    )
    INTERNAL = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.INTERNAL.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="INTERN"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="INTERN"),
        ],
    )
    EXTERNAL = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.EXTERNAL.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="EKSTERN"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="EKSTERN"),
        ],
    )
    DEPRECATED = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.DEPRECATED.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="UTGÅTT"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="UTGÅTT"),
        ],
    )


class DataSetState(LanguageStringsEnum):
    """Processing state of a dataset."""

    SOURCE_DATA = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.SOURCE_DATA.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="KILDEDATA"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="KILDEDATA"),
        ],
    )
    INPUT_DATA = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.INPUT_DATA.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="INNDATA"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="INNDATA"),
        ],
    )
    PROCESSED_DATA = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.PROCESSED_DATA.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="KLARGJORTE DATA",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="KLARGJORTE DATA",
            ),
        ],
    )
    STATISTICS = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.STATISTICS.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="STATISTIKK"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="STATISTIKK"),
        ],
    )
    OUTPUT_DATA = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.OUTPUT_DATA.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="UTDATA"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="UTDATA"),
        ],
    )


class TemporalityTypeType(LanguageStringsEnum):
    """Temporality of a dataset.

    More information about temporality type: https://statistics-norway.atlassian.net/l/c/HV12q90R
    """

    FIXED = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.FIXED.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="FAST"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="FAST"),
        ],
    )
    STATUS = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.STATUS.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="TVERRSNITT"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="TVERRSNITT"),
        ],
    )
    ACCUMULATED = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.ACCUMULATED.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="AKKUMULERT"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="AKKUMULERT"),
        ],
    )
    EVENT = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.EVENT.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="HENDELSE"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="HENDELSE"),
        ],
    )


class DataType(LanguageStringsEnum):
    """Simplified data types for metadata purposes."""

    STRING = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.STRING.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="TEKST"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="TEKST"),
        ],
    )
    INTEGER = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.INTEGER.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="HELTALL"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="HELTALL"),
        ],
    )
    FLOAT = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.FLOAT.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="DESIMALTALL"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="DESIMALTALL"),
        ],
    )
    DATETIME = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.DATETIME.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="DATOTID"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="DATOTID"),
        ],
    )
    BOOLEAN = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.BOOLEAN.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="BOOLSK"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="BOOLSK"),
        ],
    )


class IsPersonalData(LanguageStringsEnum):
    """Is the variable instance personal data and if so, how is it encrypted."""

    NOT_PERSONAL_DATA = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.IsPersonalData.NOT_PERSONAL_DATA.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="IKKE PERSONOPPLYSNING",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="IKKE PERSONOPPLYSNING",
            ),
        ],
    )
    PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.IsPersonalData.PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
        ],
    )
    NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.IsPersonalData.NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="IKKE PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="IKKE PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
        ],
    )


class VariableRole(LanguageStringsEnum):
    """The role of a variable in a dataset."""

    IDENTIFIER = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.IDENTIFIER.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="IDENTIFIKATOR",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="IDENTIFIKATOR",
            ),
        ],
    )
    MEASURE = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.MEASURE.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="MÅLEVARIABEL",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="MÅLEVARIABEL",
            ),
        ],
    )
    START_TIME = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.START_TIME.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="STARTTID"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="STARTTID"),
        ],
    )
    STOP_TIME = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.STOP_TIME.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="STOPPTID"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="STOPPTID"),
        ],
    )
    ATTRIBUTE = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.ATTRIBUTE.value,
            ),
            model.LanguageStringTypeItem(languageCode="nn", languageText="ATTRIBUTT"),
            model.LanguageStringTypeItem(languageCode="nb", languageText="ATTRIBUTT"),
        ],
    )


class UseRestriction(LanguageStringsEnum):
    """Lifecycle status of a dataset."""

    DELETION_ANONYMIZATION = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.UseRestriction.DELETION_ANONYMIZATION.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="SLETTING/ANONYMISERING",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="SLETTING/ANONYMISERING",
            ),
        ],
    )
    PROCESS_LIMITATIONS = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.UseRestriction.PROCESS_LIMITATIONS.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="BEHANDLINGSBEGRENSNINGER",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="BEHANDLINGSBEGRENSNINGER",
            ),
        ],
    )
    SECONDARY_USE_RESTRICTIONS = model.LanguageStringType(
        [
            model.LanguageStringTypeItem(
                languageCode="en",
                languageText=model.UseRestriction.SECONDARY_USE_RESTRICTIONS.value,
            ),
            model.LanguageStringTypeItem(
                languageCode="nn",
                languageText="SEKUNDÆRBRUKSRESTRIKSJONER",
            ),
            model.LanguageStringTypeItem(
                languageCode="nb",
                languageText="SEKUNDÆRBRUKSRESTRIKSJONER",
            ),
        ],
    )
