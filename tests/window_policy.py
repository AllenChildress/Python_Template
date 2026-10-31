"""Pure decisions for GUI tests. No Qt import.

The maximize fixture in conftest.py applies these. Unit tests cover them
without a display.
"""

from __future__ import annotations

from collections.abc import Mapping  # environment mapping from the fixture or a test

# Env key a human sets to pin GUI tests to one screen. Empty means primary.
TEST_SCREEN_ENV = "TEST_SCREEN"
# Qt's own platform key. offscreen is the headless value.
QT_PLATFORM_ENV = "QT_QPA_PLATFORM"
OFFSCREEN_PLATFORM = "offscreen"


def prefer_screen_name(
    requested: str | None,
    available: list[str],
    primary: str | None,
) -> str | None:
    """Pick the screen name a top-level test window should use.

    requested: the TEST_SCREEN value, or None or blank when unset.
    available: screen names the toolkit reported for this process.
    primary: the toolkit's primary screen name, or None when it has no screen.
    A requested name that is not in available falls back to primary.
    """
    name = (requested or "").strip()
    if name and name in available:
        return name
    return primary


def should_maximize(*, windowed: bool, is_window: bool) -> bool:
    """Return whether this show should maximize the widget.

    windowed: True when the test carries the windowed marker and needs an exact size.
    is_window: True when the widget is a top-level window. Child widgets keep their size.
    """
    return is_window and not windowed


def headless_platform_needed(environ: Mapping[str, str], platform: str) -> bool:
    """Return whether this test should select Qt's offscreen platform.

    environ: the process environment. A set QT_QPA_PLATFORM is left alone.
    DISPLAY or WAYLAND_DISPLAY means a display is already available.
    platform: sys.platform. Windows and macOS have a native display without DISPLAY.
    """
    if (environ.get(QT_PLATFORM_ENV) or "").strip():
        return False
    if platform.startswith("win") or platform == "darwin":
        return False
    if (environ.get("DISPLAY") or "").strip():
        return False
    if (environ.get("WAYLAND_DISPLAY") or "").strip():
        return False
    return True
