# template-owned: Python_Template
"""Startup lines: one INFO record per loaded metadata value."""

from __future__ import annotations  # postponed annotations on public signatures

import logging  # one startup line per value
from collections.abc import Mapping  # loaded rows keyed by category and variable

from src.metadata_settings.rows import Setting  # value, source, and updated date

LOGGER_NAME = "metadata.settings"


def format_loaded_line(row: Setting) -> str:
    """One startup line: value, source, and updated date.

    row: a loaded setting, including its source.
    """
    return (
        f"metadata loaded category={row.category} variable={row.variable} "
        f"value={row.value} source={row.source} updated={row.updated}"
    )


def log_loaded(logger: logging.Logger, rows: Mapping[tuple[str, str], Setting]) -> None:
    """logger: startup lines. rows: every loaded value, sidecar already merged."""
    for key in sorted(rows):
        logger.info("%s", format_loaded_line(rows[key]))
