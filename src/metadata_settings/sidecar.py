# template-owned: Python_Template
"""Write measured sidecar rows and list values that drifted from the default."""

from __future__ import annotations  # postponed annotations on public signatures

import csv  # write the sidecar table
import io  # render a CSV in memory before the atomic replace
import math  # finite-number checks for drift and tolerance
from collections.abc import Sequence  # sidecar rows handed to the writer
from dataclasses import dataclass  # one object for a measured write and its result
from pathlib import Path  # sidecar file path

from src.metadata_settings.csv_table import (  # merge after a write; refuse a directory path
    merge_rows,
    reject_directory,
)
from src.metadata_settings.rows import (  # row types, sidecar source, and MetadataError
    COLUMNS,
    SOURCE_SIDECAR,
    MetadataError,
    Setting,
    SettingDrift,
)

# Absolute numeric gap. Zero means any numeric difference is drift.
EXACT_TOLERANCE = 0.0


@dataclass(frozen=True)
class MeasuredRequest:
    """One measured write. description None keeps the previous sidecar description.

    category, variable, value: identity and measured text, not yet stripped.
    updated: ISO date the caller already took from the clock.
    """

    category: str
    variable: str
    value: str
    description: str | None
    updated: str


@dataclass(frozen=True)
class SidecarUpdate:
    """Disk and memory after one measured write.

    sidecar: full sidecar contents. merged: sidecar laid over the checked-in rows.
    saved: the row just written.
    """

    sidecar: tuple[Setting, ...]
    merged: dict[tuple[str, str], Setting]
    saved: Setting


def commit_measured(
    path: Path,
    defaults: tuple[Setting, ...],
    sidecar_rows: tuple[Setting, ...],
    request: MeasuredRequest,
) -> SidecarUpdate:
    """Write the sidecar. The checked-in file is never this path.

    path: sidecar CSV. defaults: checked-in rows, unchanged.
    sidecar_rows: current sidecar. request: the measured value and today's date.
    """
    category_key = request.category.strip()
    variable_key = request.variable.strip()
    value_text = request.value.strip()
    require_measured(category_key, variable_key, value_text)
    sidecar = upsert(
        sidecar_rows,
        category_key,
        variable_key,
        value_text,
        request.updated,
        request.description,
    )
    write_table(path, sidecar)
    merged = merge_rows(defaults, sidecar)
    return SidecarUpdate(sidecar, merged, merged[(category_key, variable_key)])


def drifts_beyond(
    defaults: tuple[Setting, ...],
    sidecar_rows: tuple[Setting, ...],
    tolerance: float,
) -> tuple[SettingDrift, ...]:
    """List sidecar values farther from the checked-in default than tolerance.

    defaults: checked-in rows. sidecar_rows: measured rows.
    tolerance: absolute numeric gap. Text values drift when the text differs.
    A sidecar key with no checked-in row is always listed.
    """
    require_tolerance(tolerance)
    by_key = {(row.category, row.variable): row for row in defaults}
    found: list[SettingDrift] = []
    for row in sorted(sidecar_rows, key=sort_key):
        drift = drift_of(by_key.get((row.category, row.variable)), row, tolerance)
        if drift is not None:
            found.append(drift)
    return tuple(found)


def drift_lines(
    defaults: tuple[Setting, ...],
    sidecar_rows: tuple[Setting, ...],
    tolerance: float,
) -> tuple[str, ...]:
    """tolerance: passed to drifts_beyond. One log line per drifting sidecar value.

    defaults and sidecar_rows: same as drifts_beyond.
    """
    lines: list[str] = []
    for drift in drifts_beyond(defaults, sidecar_rows, tolerance):
        lines.append(format_drift_line(drift))
    return tuple(lines)


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


def require_measured(category: str, variable: str, value: str) -> None:
    """category, variable, value: stripped measured identity and text."""
    if category != "" and variable != "" and value != "":
        return
    raise MetadataError("metadata: a measured value needs a category, a variable, and a value.")


def require_tolerance(tolerance: float) -> None:
    """tolerance: absolute gap. Negative and non-finite values are errors."""
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        raise MetadataError("metadata: tolerance must be a finite number >= 0.")
    if not math.isfinite(tolerance) or tolerance < 0:
        raise MetadataError("metadata: tolerance must be a finite number >= 0.")


def sort_key(row: Setting) -> tuple[str, str]:
    """row: sidecar row. Sort by category, then variable."""
    return (row.category, row.variable)


def upsert(
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
            kept.append(replaced_row(row, value, updated, description))
            replaced = True
        else:
            kept.append(row)
    if not replaced:
        text = "" if description is None else description.strip()
        kept.append(new_setting(category, variable, value, updated, text))
    return tuple(kept)


def replaced_row(row: Setting, value: str, updated: str, description: str | None) -> Setting:
    """row: the sidecar row being updated. description None keeps row.description."""
    text = row.description if description is None else description.strip()
    return new_setting(row.category, row.variable, value, updated, text)


def new_setting(category: str, variable: str, value: str, updated: str, description: str) -> Setting:
    """Build one sidecar row. Every argument is the column of the same name."""
    return Setting(
        category=category,
        variable=variable,
        value=value,
        updated=updated,
        description=description,
        source=SOURCE_SIDECAR,
    )


def write_table(path: Path, rows: Sequence[Setting]) -> None:
    """path: sidecar file. rows: full sidecar contents. The checked-in file is never this path."""
    reject_directory(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(render_csv(rows), encoding="utf-8")
        temporary.replace(path)
    except OSError as exc:
        raise MetadataError(
            f"metadata: could not write {path}. {exc}. The checked-in CSV was not touched."
        ) from exc


def render_csv(rows: Sequence[Setting]) -> str:
    """rows: sidecar rows in file order. source is omitted."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(COLUMNS), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(as_record(row))
    return buffer.getvalue()


def as_record(row: Setting) -> dict[str, str]:
    """row: one setting. Keys follow COLUMNS. source stays in memory only."""
    record: dict[str, str] = {}
    for name in COLUMNS:
        record[name] = getattr(row, name)
    return record


def drift_of(default: Setting | None, sidecar: Setting, tolerance: float) -> SettingDrift | None:
    """default: checked-in row, or None. sidecar: measured row. tolerance: numeric gap."""
    if default is None:
        return drift_record(None, sidecar)
    if default.value == sidecar.value:
        return None
    gap = numeric_gap(default.value, sidecar.value)
    if gap is not None and gap <= tolerance:
        return None
    return drift_record(default.value, sidecar)


def drift_record(default_value: str | None, sidecar: Setting) -> SettingDrift:
    """default_value: checked-in text, or None. sidecar: the measured row."""
    return SettingDrift(
        category=sidecar.category,
        variable=sidecar.variable,
        default_value=default_value,
        sidecar_value=sidecar.value,
        updated=sidecar.updated,
    )


def numeric_gap(left: str, right: str) -> float | None:
    """Absolute gap when both texts are finite numbers. None when either is not."""
    try:
        left_number = float(left)
        right_number = float(right)
    except ValueError:
        return None
    if not math.isfinite(left_number) or not math.isfinite(right_number):
        return None
    return abs(left_number - right_number)
