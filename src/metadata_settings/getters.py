# template-owned: Python_Template
"""Typed reads of one metadata cell. Callers use MetadataStore, not this module."""

from __future__ import annotations  # postponed annotations on public signatures

import math  # finite-number check for float cells
from collections.abc import Callable, Mapping  # parser, error report, and loaded rows
from dataclasses import dataclass  # one object for a typed lookup
from typing import Generic, TypeVar  # the getter's value type

from src.metadata_settings.rows import Setting  # loaded row the getter reads

T = TypeVar("T")
TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})
FALSE_TOKENS = frozenset({"0", "false", "no", "off"})


class _BadValue(Exception):
    """Cell text is not the requested type. raw is the stripped text."""

    def __init__(self, raw: str) -> None:
        """raw: the cell text that failed to parse."""
        self.raw = raw
        super().__init__(raw)


@dataclass(frozen=True)
class ValueRequest(Generic[T]):
    """One typed lookup.

    category, variable: the key.
    default: required fallback. expected: int, float, str, or bool.
    """

    category: str
    variable: str
    default: T
    expected: str


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


def read_typed(
    rows: Mapping[tuple[str, str], Setting],
    request: ValueRequest[T],
    parse: Callable[[str], T],
    report: Callable[[str], None],
) -> T:
    """Return the typed value, or the request's default after report runs.

    rows: loaded settings, sidecar already merged.
    request: category, variable, fallback, and type name.
    parse: turns cell text into T. report: log and status sentence.
    """
    row = rows.get((request.category, request.variable))
    if row is None:
        report(missing_message(request))
        return request.default
    try:
        return parse(row.value)
    except _BadValue as bad:
        report(bad_message(request, bad.raw))
        return request.default


def missing_message(request: ValueRequest[object]) -> str:
    """request: the lookup that found no row."""
    return format_setting_error(
        request.category,
        request.variable,
        missing=True,
        raw="",
        expected=request.expected,
        fallback=request.default,
    )


def bad_message(request: ValueRequest[object], raw: str) -> str:
    """request: the lookup. raw: the cell text that failed to parse."""
    return format_setting_error(
        request.category,
        request.variable,
        missing=False,
        raw=raw,
        expected=request.expected,
        fallback=request.default,
    )


def parse_int(text: str) -> int:
    """text: cell value. A whole signed integer, nothing else."""
    stripped = text.strip()
    body = stripped[1:] if stripped.startswith(("+", "-")) else stripped
    if body.isdigit() and body != "":
        return int(stripped)
    raise _BadValue(stripped)


def parse_float(text: str) -> float:
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


def parse_bool(text: str) -> bool:
    """text: cell value. Tokens are TRUE_TOKENS and FALSE_TOKENS, any case."""
    token = text.strip().lower()
    if token in TRUE_TOKENS:
        return True
    if token in FALSE_TOKENS:
        return False
    raise _BadValue(text.strip())


def parse_str(text: str) -> str:
    """text: cell value. Blank is a bad value."""
    stripped = text.strip()
    if stripped == "":
        raise _BadValue(stripped)
    return stripped
