"""Naming and sensitive-tab gate for Change_Log thumbnail promotion."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from promote_changelog_shot import (  # noqa: E402
    SENSITIVE_TABS,
    changelog_shot_filename,
    changelog_shot_markdown,
)


def test_shot_filename_includes_date_tab_and_hint() -> None:
    name = changelog_shot_filename(date(2026, 8, 13), "main", "chrome")
    assert name == "2026-08-13_main_chrome.jpg"


def test_shot_markdown_is_html_thumbnail() -> None:
    line = changelog_shot_markdown("2026-08-13_main_chrome.jpg", "2026-08-13 main chrome")
    assert 'src="changelog_shots/2026-08-13_main_chrome.jpg"' in line
    assert 'width="360"' in line


def test_sensitive_tabs_are_gated() -> None:
    assert "positions" in SENSITIVE_TABS
    assert "history" in SENSITIVE_TABS
    assert "main" not in SENSITIVE_TABS
