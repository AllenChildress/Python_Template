# template-owned: Python_Template
"""Public door for the metadata CSV loader. See docs/Metadata.md.

Callers import this package only. The sibling modules are the loader's parts.
Do not open the CSV anywhere else.
"""

from src.metadata_settings.getters import (  # typed-read errors and bool tokens
    FALSE_TOKENS,
    TRUE_TOKENS,
    format_setting_error,
)
from src.metadata_settings.rows import (  # column contract, paths, and row types
    COLUMNS,
    METADATA_DIR_NAME,
    SETTINGS_FILE_NAME,
    SIDECAR_DIR_NAME,
    SOURCE_DEFAULT,
    SOURCE_SIDECAR,
    MetadataError,
    Setting,
    SettingDrift,
    StatusBar,
    checkout_root,
    defaults_path,
    sidecar_path,
)
from src.metadata_settings.sidecar import (  # drift tolerance and sidecar log lines
    EXACT_TOLERANCE,
    format_drift_line,
    format_sidecar_write_line,
)
from src.metadata_settings.startup_log import (  # startup logger name and line format
    LOGGER_NAME,
    format_loaded_line,
)
from src.metadata_settings.store import MetadataStore  # the only loader object
from src.runtime_flags import running_under_tests  # re-export; store calls its own binding

__all__ = (
    "COLUMNS",
    "EXACT_TOLERANCE",
    "FALSE_TOKENS",
    "LOGGER_NAME",
    "METADATA_DIR_NAME",
    "SETTINGS_FILE_NAME",
    "SIDECAR_DIR_NAME",
    "SOURCE_DEFAULT",
    "SOURCE_SIDECAR",
    "TRUE_TOKENS",
    "MetadataError",
    "MetadataStore",
    "Setting",
    "SettingDrift",
    "StatusBar",
    "checkout_root",
    "defaults_path",
    "format_drift_line",
    "format_loaded_line",
    "format_setting_error",
    "format_sidecar_write_line",
    "running_under_tests",
    "sidecar_path",
)
