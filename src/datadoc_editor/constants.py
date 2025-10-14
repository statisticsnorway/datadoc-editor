"""Repository for constant values in Datadoc."""

MISSING_METADATA_WARNING = "Advarsel - obligatorisk metadata mangler"
CHECK_OBLIGATORY_METADATA_DATASET_MESSAGE = "Følgende datasett felt har ikke verdi:"
CHECK_OBLIGATORY_METADATA_VARIABLES_MESSAGE = "Følgende variabler har felt uten verdi:"
DAPLA_MANUAL_TEXT = "Dapla manual navnestandard"

ILLEGAL_SHORTNAME_WARNING = (
    "Noen av variablene i datasetter følger ikke navnestandard for kortnavn"
)
ILLEGAL_SHORTNAME_WARNING_MESSAGE = "Følgende navnestandard er utarbeidet for variabler: Alfanumerisk begrenset til a-z (kun små bokstaver), 0-9 og _ (understrek). Kortnavn som ikke følger standarden:"

STANDARD_ALGORITM_DAPLA_ENCRYPTION = "TINK-DAEAD"
PAPIS_ALGORITHM_ENCRYPTION = "TINK-FPE"
PAPIS_STABLE_IDENTIFIER_TYPE = "FREG_SNR"
PAPIS_ENCRYPTION_KEY_REFERENCE = "papis-common-key-1"
DAEAD_ENCRYPTION_KEY_REFERENCE = "ssb-common-key-1"
ENCRYPTION_PARAMETER_SNAPSHOT_DATE = "snapshotDate"
ENCRYPTION_PARAMETER_KEY_ID = "keyId"
ENCRYPTION_PARAMETER_STRATEGY = "strategy"
ENCRYPTION_PARAMETER_STRATEGY_SKIP = "skip"
