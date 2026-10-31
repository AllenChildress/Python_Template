# template-owned: Python_Template
"""Read the settings CSVs and merge a sidecar over the checked-in rows."""

from __future__ import annotations  # postponed annotations on public signatures

import csv  # read the settings tables
import io  # parse a CSV body that was already read as text
from collections.abc import Mapping, Sequence  # header cells and raw DictReader rows
from pathlib import Path  # checked-in CSV and sidecar file paths

from src.metadata_settings.rows import (  # row type, columns, and MetadataError
    COLUMNS,
    MetadataError,
    Setting,
)


def read_table(path: Path, *, required: bool, source: str) -> tuple[Setting, ...]:
    """path: CSV file. required: a missing file raises when True. source: stamped on each row."""
    reject_directory(path)
    if not path.is_file():
        if required:
            raise MetadataError(
                f"metadata: missing {path}. Checked-in defaults belong in metadata/settings.csv."
            )
        return ()
    return parse_table(read_text(path), path, source)


def merge_rows(
    defaults: tuple[Setting, ...],
    sidecar: tuple[Setting, ...],
) -> dict[tuple[str, str], Setting]:
    """Sidecar rows replace checked-in rows with the same category and variable."""
    merged = {(row.category, row.variable): row for row in defaults}
    for row in sidecar:
        merged[(row.category, row.variable)] = row
    return merged


def reject_directory(path: Path) -> None:
    """path: expected CSV file. A directory at that path is a broken layout."""
    if path.is_dir():
        raise MetadataError(f"metadata: {path} is a directory. Expected a CSV file.")


def read_text(path: Path) -> str:
    """path: CSV file to read as UTF-8, accepting a leading BOM."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise MetadataError(f"metadata: could not read {path}. {exc}.") from exc


def parse_table(text: str, path: Path, source: str) -> tuple[Setting, ...]:
    """text: CSV body. path: used in errors. source: checked-in default or sidecar override."""
    if text.strip() == "":
        raise MetadataError(f"metadata: {path} is empty. Expected header {','.join(COLUMNS)}.")
    reader = csv.DictReader(io.StringIO(text))
    require_columns(reader.fieldnames, path)
    return rows_from_reader(reader, path, source)


def require_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    """fieldnames: header cells. path: used in the error."""
    found = tuple(fieldnames or ())
    if found != COLUMNS:
        raise MetadataError(
            f"metadata: {path} header is {','.join(found)!r}; expected {','.join(COLUMNS)!r}."
        )


def rows_from_reader(
    reader: csv.DictReader[str],
    path: Path,
    source: str,
) -> tuple[Setting, ...]:
    """reader: positioned after the header. path and source: stamped onto each row and error."""
    rows: list[Setting] = []
    seen: set[tuple[str, str]] = set()
    for raw in reader:
        row = row_from_mapping(raw, path, source)
        key = (row.category, row.variable)
        if key in seen:
            raise MetadataError(f"metadata: {path} repeats {row.category}.{row.variable}.")
        seen.add(key)
        rows.append(row)
    return tuple(rows)


def row_from_mapping(raw: Mapping[str, str | None], path: Path, source: str) -> Setting:
    """raw: one DictReader row. path: used in the error. source: where the row was read."""
    category = cell(raw, "category")
    variable = cell(raw, "variable")
    updated = cell(raw, "updated")
    if category == "" or variable == "" or updated == "":
        raise MetadataError(f"metadata: {path} has a row missing category, variable, or updated.")
    return Setting(
        category=category,
        variable=variable,
        value=cell(raw, "value"),
        updated=updated,
        description=cell(raw, "description"),
        source=source,
    )


def cell(raw: Mapping[str, str | None], name: str) -> str:
    """raw: one CSV row. name: column."""
    return (raw.get(name) or "").strip()
