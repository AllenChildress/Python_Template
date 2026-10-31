# template-owned: Python_Template
"""MetadataStore: the object callers use. Parts live in the sibling modules."""

from __future__ import annotations  # postponed annotations on public signatures

import logging  # startup lines and errors for missing or bad values
from collections.abc import Callable  # clock hook and cell parsers
from datetime import date  # sidecar updated column is an ISO date
from pathlib import Path  # checked-in CSV and sidecar paths
from typing import TypeVar  # getter return type on MetadataStore._read

from src.metadata_settings.csv_table import merge_rows, read_table  # load both CSVs and overlay
from src.metadata_settings.getters import (  # typed reads and the bool/number parsers
    ValueRequest,
    parse_bool,
    parse_float,
    parse_int,
    parse_str,
    read_typed,
)
from src.metadata_settings.rows import (  # paths, errors, and the status-bar hook
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
from src.metadata_settings.sidecar import (  # measured writes and drift listing
    MeasuredRequest,
    commit_measured,
    drift_lines as sidecar_drift_lines,
    drifts_beyond as sidecar_drifts_beyond,
    format_sidecar_write_line,
)
from src.metadata_settings.startup_log import LOGGER_NAME, log_loaded  # one startup line per value
from src.runtime_flags import running_under_tests  # tests must not touch the checkout sidecar

T = TypeVar("T")


class MetadataStore:
    """Checked-in metadata CSV plus an optional measured sidecar.

    Typed getters are the only read API. write_measured updates the sidecar.
    The checked-in file is never written. Import this class from src.metadata_settings.
    """

    def __init__(
        self,
        defaults_path: Path,
        sidecar_path: Path,
        *,
        logger: logging.Logger | None = None,
        status: StatusBar | None = None,
        today: Callable[[], date] | None = None,
    ) -> None:
        """defaults_path: checked-in CSV. sidecar_path: gitignored measured CSV.

        logger: startup and error lines. None uses LOGGER_NAME.
        status: app status bar. None logs only.
        today: clock for sidecar writes. None uses date.today.
        """
        self._defaults_path = defaults_path
        self._sidecar_path = sidecar_path
        self._logger = logging.getLogger(LOGGER_NAME) if logger is None else logger
        self._status = status
        self._today = date.today if today is None else today
        self._defaults: tuple[Setting, ...] = ()
        self._sidecar: tuple[Setting, ...] = ()
        self._rows: dict[tuple[str, str], Setting] = {}
        self._loaded = False

    @classmethod
    def from_root(
        cls,
        root: Path,
        *,
        logger: logging.Logger | None = None,
        status: StatusBar | None = None,
        today: Callable[[], date] | None = None,
    ) -> MetadataStore:
        """root: directory that contains metadata/.

        logger, status, today: same as MetadataStore.
        """
        resolved = root.resolve()
        if running_under_tests() and resolved == checkout_root():
            raise MetadataError(
                "running_under_tests: pass a temporary root. "
                "Loading the checkout would read metadata/local."
            )
        return cls(
            defaults_path(resolved),
            sidecar_path(resolved),
            logger=logger,
            status=status,
            today=today,
        )

    def load(self) -> None:
        """Read both CSVs and log every loaded value. Call once at startup."""
        try:
            self._refuse_checkout_sidecar()
            defaults = read_table(self._defaults_path, required=True, source=SOURCE_DEFAULT)
            sidecar = read_table(self._sidecar_path, required=False, source=SOURCE_SIDECAR)
        except MetadataError as exc:
            self._emit_error(str(exc))
            raise
        self._defaults = defaults
        self._sidecar = sidecar
        self._rows = merge_rows(defaults, sidecar)
        self._loaded = True
        log_loaded(self._logger, self._rows)

    def get_str(self, category: str, variable: str, default: str) -> str:
        """Return the text for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or blank.
        """
        return self._read(category, variable, default, parse_str, "str")

    def get_int(self, category: str, variable: str, default: int) -> int:
        """Return the integer for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or not an integer.
        """
        return self._read(category, variable, default, parse_int, "int")

    def get_float(self, category: str, variable: str, default: float) -> float:
        """Return the number for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or not a finite number.
        """
        return self._read(category, variable, default, parse_float, "float")

    def get_bool(self, category: str, variable: str, default: bool) -> bool:
        """Return the bool for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or not a bool token.
        """
        return self._read(category, variable, default, parse_bool, "bool")

    def write_measured(
        self,
        category: str,
        variable: str,
        value: str,
        description: str | None = None,
    ) -> None:
        """Record a measured value in the sidecar. Sets updated to today.

        category, variable: identity of the setting.
        value: measured text. The checked-in CSV is never written.
        description: replacement text. None keeps the description already in the sidecar.
        """
        self._ensure_loaded()
        try:
            self._refuse_checkout_sidecar()
            saved = commit_measured(
                self._sidecar_path,
                self._defaults,
                self._sidecar,
                MeasuredRequest(category, variable, value, description, self._today().isoformat()),
            )
        except MetadataError as exc:
            self._emit_error(str(exc))
            raise
        self._sidecar = saved.sidecar
        self._rows = saved.merged
        self._logger.info("%s", format_sidecar_write_line(saved.saved))

    def drifts_beyond(self, tolerance: float) -> tuple[SettingDrift, ...]:
        """List sidecar values farther from the checked-in default than tolerance.

        tolerance: absolute numeric gap. Text values drift when the text differs.
        A sidecar key with no checked-in row is always listed.
        """
        self._ensure_loaded()
        return sidecar_drifts_beyond(self._defaults, self._sidecar, tolerance)

    def drift_lines(self, tolerance: float) -> tuple[str, ...]:
        """tolerance: passed to drifts_beyond. One log line per drifting sidecar value."""
        self._ensure_loaded()
        return sidecar_drift_lines(self._defaults, self._sidecar, tolerance)

    def _ensure_loaded(self) -> None:
        """Load on first use so a getter still logs the startup lines."""
        if not self._loaded:
            self.load()

    def _read(
        self,
        category: str,
        variable: str,
        default: T,
        parse: Callable[[str], T],
        expected: str,
    ) -> T:
        """category, variable: lookup key. default: required fallback.

        parse: turns cell text into T. expected: int, float, str, or bool.
        """
        self._ensure_loaded()
        return read_typed(
            self._rows,
            ValueRequest(category, variable, default, expected),
            parse,
            self._emit_error,
        )

    def _emit_error(self, message: str) -> None:
        """message: sentence for the log and, when present, the status bar."""
        self._logger.error("%s", message)
        if self._status is not None:
            self._status.show_error(message)

    def _refuse_checkout_sidecar(self) -> None:
        """Tests write under tmp_path, not the checkout's metadata/local tree."""
        # Lesson: a test that writes metadata/local dirties the checkout the next session sees.
        if not running_under_tests():
            return
        folder = sidecar_path(checkout_root()).parent.resolve()
        candidate = self._sidecar_path.resolve()
        if candidate == folder or candidate.is_relative_to(folder):
            raise MetadataError(
                "running_under_tests: measured values stay in a temporary directory, "
                "not metadata/local in the checkout."
            )
