# template-owned: Python_Template
"""Load non-user tuning from one CSV. See docs/Metadata.md.

Checked-in defaults live at metadata/settings.csv. The app may write measured
values only under metadata/local/. Callers use this module. No ad hoc CSV reads.
"""

from __future__ import annotations  # postponed annotations on public signatures

import csv  # read and write the settings tables
import io  # render a CSV in memory before the atomic replace
import logging  # one startup line per value, and errors for missing or bad values
import math  # finite-number checks for floats, drift, and tolerance
from collections.abc import Callable, Mapping, Sequence  # clock, CSV rows, row maps
from dataclasses import dataclass  # one object per setting and per drift row
from datetime import date  # sidecar updated column is an ISO date
from pathlib import Path  # checked-in CSV, sidecar, and checkout root
from typing import Protocol, TypeVar  # status bar hook and typed getter return

from src.runtime_flags import running_under_tests  # tests must not touch the checkout sidecar

# Column order is the file contract. Projects keep this header.
COLUMNS = ("category", "variable", "value", "updated", "description")
METADATA_DIR_NAME = "metadata"
SETTINGS_FILE_NAME = "settings.csv"
SIDECAR_DIR_NAME = "local"
SOURCE_DEFAULT = "checked-in default"
SOURCE_SIDECAR = "sidecar override"
LOGGER_NAME = "metadata.settings"
# Absolute numeric gap. Zero means any numeric difference is drift.
EXACT_TOLERANCE = 0.0
TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})
FALSE_TOKENS = frozenset({"0", "false", "no", "off"})

T = TypeVar("T")


class MetadataError(Exception):
    """A settings file is unreadable, or a measured write was refused."""


class _BadValue(Exception):
    """Cell text is not the requested type. raw is the stripped text."""

    def __init__(self, raw: str) -> None:
        """raw: the cell text that failed to parse."""
        self.raw = raw
        super().__init__(raw)


class StatusBar(Protocol):
    """Status line the app already shows. The loader calls it on a bad read."""

    def show_error(self, message: str) -> None:
        """message: the same sentence written to the error log."""


@dataclass(frozen=True)
class Setting:
    """One metadata row plus which file supplied it.

    category, variable, value, updated, description: the CSV columns.
    source: checked-in default or sidecar override. Not a CSV column.
    """

    category: str
    variable: str
    value: str
    updated: str
    description: str
    source: str


@dataclass(frozen=True)
class SettingDrift:
    """One sidecar value farther from the checked-in default than the tolerance.

    default_value is None when the sidecar key has no checked-in row.
    """

    category: str
    variable: str
    default_value: str | None
    sidecar_value: str
    updated: str


def checkout_root() -> Path:
    """Repo root. This file lives at src/metadata_settings.py."""
    return Path(__file__).resolve().parents[1]


def defaults_path(root: Path) -> Path:
    """root: checkout or a temporary copy. Returns metadata/settings.csv."""
    return root / METADATA_DIR_NAME / SETTINGS_FILE_NAME


def sidecar_path(root: Path) -> Path:
    """root: checkout or a temporary copy. Returns metadata/local/settings.csv."""
    return root / METADATA_DIR_NAME / SIDECAR_DIR_NAME / SETTINGS_FILE_NAME


def format_loaded_line(row: Setting) -> str:
    """One startup line: value, source, and updated date.

    row: a loaded setting, including its source.
    """
    return (
        f"metadata loaded category={row.category} variable={row.variable} "
        f"value={row.value} source={row.source} updated={row.updated}"
    )


def format_sidecar_write_line(row: Setting) -> str:
    """One line after a measured write. row: the sidecar row just saved."""
    return (
        f"metadata sidecar wrote category={row.category} variable={row.variable} "
        f"value={row.value} source={row.source} updated={row.updated}"
    )


def format_drift_line(drift: SettingDrift) -> str:
    """drift: one sidecar row that is outside tolerance."""
    default = "(none)" if drift.default_value is None else drift.default_value
    return (
        f"metadata drift category={drift.category} variable={drift.variable} "
        f"default={default} sidecar={drift.sidecar_value} updated={drift.updated}"
    )


def format_setting_error(
    category: str,
    variable: str,
    *,
    missing: bool,
    raw: str,
    expected: str,
    fallback: object,
) -> str:
    """One sentence for the log and the status bar.

    category, variable: the setting that failed.
    missing: True when the row is absent. False when the value does not parse.
    raw: the text that failed to parse. Ignored when missing is True.
    expected: int, float, str, or bool.
    fallback: the default the caller required.
    """
    name = f"{category}.{variable}"
    if missing:
        return f"metadata: missing setting {name} ({expected}); using default {fallback!r}"
    return (
        f"metadata: bad value for {name}: {raw!r} is not {expected}; "
        f"using default {fallback!r}"
    )


class MetadataStore:
    """Checked-in metadata CSV plus an optional measured sidecar.

    Typed getters are the only read API. write_measured updates the sidecar.
    The checked-in file is never written.
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
            defaults = _read_table(self._defaults_path, required=True, source=SOURCE_DEFAULT)
            sidecar = _read_table(self._sidecar_path, required=False, source=SOURCE_SIDECAR)
        except MetadataError as exc:
            self._emit_error(str(exc))
            raise
        self._defaults = defaults
        self._sidecar = sidecar
        self._rows = _merge(defaults, sidecar)
        self._loaded = True
        self._log_loaded()

    def get_str(self, category: str, variable: str, default: str) -> str:
        """Return the text for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or blank.
        """
        return self._read(category, variable, default, _parse_str, "str")

    def get_int(self, category: str, variable: str, default: int) -> int:
        """Return the integer for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or not an integer.
        """
        return self._read(category, variable, default, _parse_int, "int")

    def get_float(self, category: str, variable: str, default: float) -> float:
        """Return the number for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or not a finite number.
        """
        return self._read(category, variable, default, _parse_float, "float")

    def get_bool(self, category: str, variable: str, default: bool) -> bool:
        """Return the bool for category and variable.

        category, variable: lookup key.
        default: required fallback when the setting is missing or not a bool token.
        """
        return self._read(category, variable, default, _parse_bool, "bool")

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
            saved = self._commit_measured(category, variable, value, description)
        except MetadataError as exc:
            self._emit_error(str(exc))
            raise
        self._logger.info("%s", format_sidecar_write_line(saved))

    def drifts_beyond(self, tolerance: float) -> tuple[SettingDrift, ...]:
        """List sidecar values farther from the checked-in default than tolerance.

        tolerance: absolute numeric gap. Text values drift when the text differs.
        A sidecar key with no checked-in row is always listed.
        """
        self._ensure_loaded()
        _require_tolerance(tolerance)
        defaults = {(row.category, row.variable): row for row in self._defaults}
        found: list[SettingDrift] = []
        for row in sorted(self._sidecar, key=_sort_key):
            drift = _drift_of(defaults.get((row.category, row.variable)), row, tolerance)
            if drift is not None:
                found.append(drift)
        return tuple(found)

    def drift_lines(self, tolerance: float) -> tuple[str, ...]:
        """tolerance: passed to drifts_beyond. One log line per drifting sidecar value."""
        lines: list[str] = []
        for drift in self.drifts_beyond(tolerance):
            lines.append(format_drift_line(drift))
        return tuple(lines)

    def _ensure_loaded(self) -> None:
        """Load on first use so a getter still logs the startup lines."""
        if not self._loaded:
            self.load()

    def _log_loaded(self) -> None:
        """One INFO line per loaded value, with source and updated date."""
        for key in sorted(self._rows):
            self._logger.info("%s", format_loaded_line(self._rows[key]))

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
        row = self._rows.get((category, variable))
        if row is None:
            self._report_bad(category, variable, missing=True, raw="", expected=expected, fallback=default)
            return default
        try:
            return parse(row.value)
        except _BadValue as bad:
            self._report_bad(
                category,
                variable,
                missing=False,
                raw=bad.raw,
                expected=expected,
                fallback=default,
            )
            return default

    def _report_bad(
        self,
        category: str,
        variable: str,
        *,
        missing: bool,
        raw: str,
        expected: str,
        fallback: object,
    ) -> None:
        """Log and show a missing or bad value. The caller still receives fallback.

        category, variable, missing, raw, expected, fallback: same as format_setting_error.
        """
        message = format_setting_error(
            category,
            variable,
            missing=missing,
            raw=raw,
            expected=expected,
            fallback=fallback,
        )
        self._emit_error(message)

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
        folder = (checkout_root() / METADATA_DIR_NAME / SIDECAR_DIR_NAME).resolve()
        candidate = self._sidecar_path.resolve()
        if candidate == folder or candidate.is_relative_to(folder):
            raise MetadataError(
                "running_under_tests: measured values stay in a temporary directory, "
                "not metadata/local in the checkout."
            )

    def _commit_measured(
        self,
        category: str,
        variable: str,
        value: str,
        description: str | None,
    ) -> Setting:
        """Write the sidecar, then refresh memory. Returns the saved row.

        category, variable, value, description: same as write_measured.
        """
        self._refuse_checkout_sidecar()
        category_key = category.strip()
        variable_key = variable.strip()
        value_text = value.strip()
        _require_measured(category_key, variable_key, value_text)
        updated = self._today().isoformat()
        sidecar = _upsert(
            self._sidecar,
            category_key,
            variable_key,
            value_text,
            updated,
            description,
        )
        _write_table(self._sidecar_path, sidecar)
        self._sidecar = sidecar
        self._rows = _merge(self._defaults, sidecar)
        return self._rows[(category_key, variable_key)]


def _sort_key(row: Setting) -> tuple[str, str]:
    """row: sidecar row. Sort by category, then variable."""
    return (row.category, row.variable)


def _require_measured(category: str, variable: str, value: str) -> None:
    """category, variable, value: stripped measured identity and text."""
    if category != "" and variable != "" and value != "":
        return
    raise MetadataError("metadata: a measured value needs a category, a variable, and a value.")


def _require_tolerance(tolerance: float) -> None:
    """tolerance: absolute gap. Negative and non-finite values are errors."""
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        raise MetadataError("metadata: tolerance must be a finite number >= 0.")
    if not math.isfinite(tolerance) or tolerance < 0:
        raise MetadataError("metadata: tolerance must be a finite number >= 0.")


def _read_table(path: Path, *, required: bool, source: str) -> tuple[Setting, ...]:
    """path: CSV file. required: a missing file raises when True. source: stamped on each row."""
    _reject_directory(path)
    if not path.is_file():
        if required:
            raise MetadataError(
                f"metadata: missing {path}. Checked-in defaults belong in metadata/settings.csv."
            )
        return ()
    return _parse_table(_read_text(path), path, source)


def _reject_directory(path: Path) -> None:
    """path: expected CSV file. A directory at that path is a broken layout."""
    if path.is_dir():
        raise MetadataError(f"metadata: {path} is a directory. Expected a CSV file.")


def _read_text(path: Path) -> str:
    """path: CSV file to read as UTF-8, accepting a leading BOM."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise MetadataError(f"metadata: could not read {path}. {exc}.") from exc


def _parse_table(text: str, path: Path, source: str) -> tuple[Setting, ...]:
    """text: CSV body. path: used in errors. source: checked-in default or sidecar override."""
    if text.strip() == "":
        raise MetadataError(f"metadata: {path} is empty. Expected header {','.join(COLUMNS)}.")
    reader = csv.DictReader(io.StringIO(text))
    _require_columns(reader.fieldnames, path)
    return _rows_from_reader(reader, path, source)


def _require_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    """fieldnames: header cells. path: used in the error."""
    found = tuple(fieldnames or ())
    if found != COLUMNS:
        raise MetadataError(
            f"metadata: {path} header is {','.join(found)!r}; expected {','.join(COLUMNS)!r}."
        )


def _rows_from_reader(
    reader: csv.DictReader[str],
    path: Path,
    source: str,
) -> tuple[Setting, ...]:
    """reader: positioned after the header. path and source: stamped onto each row and error."""
    rows: list[Setting] = []
    seen: set[tuple[str, str]] = set()
    for raw in reader:
        row = _row_from_mapping(raw, path, source)
        key = (row.category, row.variable)
        if key in seen:
            raise MetadataError(f"metadata: {path} repeats {row.category}.{row.variable}.")
        seen.add(key)
        rows.append(row)
    return tuple(rows)


def _row_from_mapping(raw: Mapping[str, str | None], path: Path, source: str) -> Setting:
    """raw: one DictReader row. path: used in the error. source: where the row was read."""
    category = _cell(raw, "category")
    variable = _cell(raw, "variable")
    updated = _cell(raw, "updated")
    if category == "" or variable == "" or updated == "":
        raise MetadataError(f"metadata: {path} has a row missing category, variable, or updated.")
    return Setting(
        category=category,
        variable=variable,
        value=_cell(raw, "value"),
        updated=updated,
        description=_cell(raw, "description"),
        source=source,
    )


def _cell(raw: Mapping[str, str | None], name: str) -> str:
    """raw: one CSV row. name: column."""
    return (raw.get(name) or "").strip()


def _merge(
    defaults: tuple[Setting, ...],
    sidecar: tuple[Setting, ...],
) -> dict[tuple[str, str], Setting]:
    """Sidecar rows replace checked-in rows with the same category and variable."""
    merged = {(row.category, row.variable): row for row in defaults}
    for row in sidecar:
        merged[(row.category, row.variable)] = row
    return merged


def _upsert(
    rows: tuple[Setting, ...],
    category: str,
    variable: str,
    value: str,
    updated: str,
    description: str | None,
) -> tuple[Setting, ...]:
    """rows: current sidecar. description None keeps the previous description."""
    kept: list[Setting] = []
    replaced = False
    for row in rows:
        if row.category == category and row.variable == variable:
            kept.append(_replaced(row, value, updated, description))
            replaced = True
        else:
            kept.append(row)
    if not replaced:
        text = "" if description is None else description.strip()
        kept.append(_new_setting(category, variable, value, updated, text))
    return tuple(kept)


def _replaced(row: Setting, value: str, updated: str, description: str | None) -> Setting:
    """row: the sidecar row being updated. description None keeps row.description."""
    text = row.description if description is None else description.strip()
    return _new_setting(row.category, row.variable, value, updated, text)


def _new_setting(category: str, variable: str, value: str, updated: str, description: str) -> Setting:
    """Build one sidecar row. Every argument is the column of the same name."""
    return Setting(
        category=category,
        variable=variable,
        value=value,
        updated=updated,
        description=description,
        source=SOURCE_SIDECAR,
    )


def _write_table(path: Path, rows: Sequence[Setting]) -> None:
    """path: sidecar file. rows: full sidecar contents. The checked-in file is never this path."""
    _reject_directory(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(_render_csv(rows), encoding="utf-8")
        temporary.replace(path)
    except OSError as exc:
        raise MetadataError(
            f"metadata: could not write {path}. {exc}. The checked-in CSV was not touched."
        ) from exc


def _render_csv(rows: Sequence[Setting]) -> str:
    """rows: sidecar rows in file order. source is omitted."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(COLUMNS), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(_as_record(row))
    return buffer.getvalue()


def _as_record(row: Setting) -> dict[str, str]:
    """row: one setting. Keys follow COLUMNS. source stays in memory only."""
    record: dict[str, str] = {}
    for name in COLUMNS:
        record[name] = getattr(row, name)
    return record


def _drift_of(default: Setting | None, sidecar: Setting, tolerance: float) -> SettingDrift | None:
    """default: checked-in row, or None. sidecar: measured row. tolerance: numeric gap."""
    if default is None:
        return _drift_record(None, sidecar)
    if default.value == sidecar.value:
        return None
    gap = _numeric_gap(default.value, sidecar.value)
    if gap is not None and gap <= tolerance:
        return None
    return _drift_record(default.value, sidecar)


def _drift_record(default_value: str | None, sidecar: Setting) -> SettingDrift:
    """default_value: checked-in text, or None. sidecar: the measured row."""
    return SettingDrift(
        category=sidecar.category,
        variable=sidecar.variable,
        default_value=default_value,
        sidecar_value=sidecar.value,
        updated=sidecar.updated,
    )


def _numeric_gap(left: str, right: str) -> float | None:
    """Absolute gap when both texts are finite numbers. None when either is not."""
    try:
        left_number = float(left)
        right_number = float(right)
    except ValueError:
        return None
    if not math.isfinite(left_number) or not math.isfinite(right_number):
        return None
    return abs(left_number - right_number)


def _parse_int(text: str) -> int:
    """text: cell value. A whole signed integer, nothing else."""
    stripped = text.strip()
    body = stripped[1:] if stripped.startswith(("+", "-")) else stripped
    if body.isdigit() and body != "":
        return int(stripped)
    raise _BadValue(stripped)


def _parse_float(text: str) -> float:
    """text: cell value. A finite number."""
    stripped = text.strip()
    if stripped == "":
        raise _BadValue(stripped)
    try:
        number = float(stripped)
    except ValueError as exc:
        raise _BadValue(stripped) from exc
    if not math.isfinite(number):
        raise _BadValue(stripped)
    return number


def _parse_bool(text: str) -> bool:
    """text: cell value. Tokens are TRUE_TOKENS and FALSE_TOKENS, any case."""
    token = text.strip().lower()
    if token in TRUE_TOKENS:
        return True
    if token in FALSE_TOKENS:
        return False
    raise _BadValue(text.strip())


def _parse_str(text: str) -> str:
    """text: cell value. Blank is a bad value."""
    stripped = text.strip()
    if stripped == "":
        raise _BadValue(stripped)
    return stripped
