"""Screen choice, maximize policy, and headless selection. No Qt."""

from __future__ import annotations

from tests.window_policy import (  # pure decisions the window fixture applies
    headless_platform_needed,
    prefer_screen_name,
    should_maximize,
)


def test_blank_request_uses_the_primary_screen() -> None:
    """requested is blank: no TEST_SCREEN override, so the primary screen wins.

    available: two screens the toolkit reported. primary: the first of them.
    """
    chosen = prefer_screen_name("", ["HDMI-1", "DP-1"], "HDMI-1")
    assert chosen == "HDMI-1"


def test_named_request_wins_when_that_screen_exists() -> None:
    """requested: the TEST_SCREEN name the human set. available includes it."""
    chosen = prefer_screen_name("DP-1", ["HDMI-1", "DP-1"], "HDMI-1")
    assert chosen == "DP-1"


def test_unknown_request_falls_back_to_primary() -> None:
    """requested names a screen that is not in available."""
    chosen = prefer_screen_name("GONE", ["HDMI-1"], "HDMI-1")
    assert chosen == "HDMI-1"


def test_windowed_marker_keeps_the_exact_size() -> None:
    """windowed True: this test opted out of maximize. is_window True: top-level."""
    assert should_maximize(windowed=True, is_window=True) is False


def test_top_level_window_maximizes_by_default() -> None:
    """windowed False and is_window True: the default for a top-level test window."""
    assert should_maximize(windowed=False, is_window=True) is True


def test_child_widget_keeps_its_size() -> None:
    """is_window False: a child keeps the size its parent assigned."""
    assert should_maximize(windowed=False, is_window=False) is False


def test_linux_without_a_display_uses_offscreen() -> None:
    """environ has no display variables. platform is linux."""
    assert headless_platform_needed({}, "linux") is True


def test_whitespace_platform_still_counts_as_unset() -> None:
    """environ QT_QPA_PLATFORM is blank. platform is linux, with no display."""
    assert headless_platform_needed({"QT_QPA_PLATFORM": "  "}, "linux") is True


def test_explicit_platform_is_left_alone() -> None:
    """environ QT_QPA_PLATFORM already names the plugin."""
    assert headless_platform_needed({"QT_QPA_PLATFORM": "offscreen"}, "linux") is False


def test_windows_keeps_the_native_platform() -> None:
    """platform win32: a desktop session has a display without DISPLAY."""
    assert headless_platform_needed({}, "win32") is False


def test_linux_display_keeps_the_native_platform() -> None:
    """environ DISPLAY is set, so a person can watch the window."""
    assert headless_platform_needed({"DISPLAY": ":0"}, "linux") is False


def test_wayland_display_keeps_the_native_platform() -> None:
    """environ WAYLAND_DISPLAY is set. platform is linux."""
    assert headless_platform_needed({"WAYLAND_DISPLAY": "wayland-0"}, "linux") is False
