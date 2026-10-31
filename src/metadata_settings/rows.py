# template-owned: Python_Template
"""Rows, paths, and errors shared by the metadata loader. See docs/Metadata.md."""

from __future__ import annotations  # postponed annotations on public signatures

from dataclasses import dataclass  # one object per setting and per drift row
from pathlib import Path  # checked-in CSV, sidecar, and checkout root
from typing import Protocol  # status bar hook with no UI import

# Column order is the file contract. Projects keep this header.
COLUMNS = ("category", "variable", "value", "updated", "description")
METADATA_DIR_NAME = "metadata"
SETTINGS_FILE_NAME = "settings.csv"
SIDECAR_DIR_NAME = "local"
SOURCE_DEFAULT = "checked-in default"
SOURCE_SIDECAR = "sidecar override"


class MetadataError(Exception):
    """A settings file is unreadable, or a measured write was refused."""


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
    """Repo root. This file lives at src/metadata_settings/rows.py."""
    return Path(__file__).resolve().parents[2]


def defaults_path(root: Path) -> Path:
    """root: checkout or a temporary copy. Returns metadata/settings.csv."""
    return root / METADATA_DIR_NAME / SETTINGS_FILE_NAME


def sidecar_path(root: Path) -> Path:
    """root: checkout or a temporary copy. Returns metadata/local/settings.csv."""
    return root / METADATA_DIR_NAME / SIDECAR_DIR_NAME / SETTINGS_FILE_NAME
