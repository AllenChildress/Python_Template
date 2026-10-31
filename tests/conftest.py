"""Shared pytest fixtures.

Qt is optional. When no binding imports, the window fixture does nothing so
``python -m pytest tests/unit -q`` still passes without PySide or PyQt.
"""

from __future__ import annotations

import os  # TEST_SCREEN and QT_QPA_PLATFORM for this test only
import sys  # sys.platform decides whether Linux needs the offscreen plugin
from collections.abc import Iterator  # fixture yields once, then closes widgets

import pytest  # fixtures, markers, and monkeypatch

from tests.window_policy import (  # pure screen and headless decisions, no Qt
    OFFSCREEN_PLATFORM,
    QT_PLATFORM_ENV,
    TEST_SCREEN_ENV,
    headless_platform_needed,
    prefer_screen_name,
    should_maximize,
)

# First binding that imports wins. A miss is a missing optional dependency.
_QT_WIDGET_MODULES = (
    "PySide6.QtWidgets",
    "PyQt6.QtWidgets",
    "PySide2.QtWidgets",
    "PyQt5.QtWidgets",
)

_qt_widgets: object | None = None
_qt_checked = False
# Ids of widgets inside the wrapped show. Discarded before the next call.
_SHOWING: set[int] = set()


def pytest_configure(config: pytest.Config) -> None:
    """Register kit markers.

    config: pytest's config object. Each line is a marker name and its meaning.
    """
    config.addinivalue_line(
        "markers",
        "windowed: keep an exact window size; skip the default maximize-on-one-screen behavior",
    )
    config.addinivalue_line(
        "markers",
        "smoke: key components work — the app boots and reaches important places (external services, database, each core feature). Early warning before production users. Skip with a reason when a service is down",
    )
    config.addinivalue_line(
        "markers",
        "integration: the whole app from the start through key parts; generally the happy path",
    )
    config.addinivalue_line(
        "markers",
        "network: contacts the network; keep it out of the default unit run",
    )
    config.addinivalue_line(
        "markers",
        "regression: the edge cases",
    )


def _load_qt_widgets() -> object | None:
    """Return a Qt widgets module, or None when no binding imports.

    No parameters. A failed import is a missing optional dependency.
    The first success is cached so later tests do not import again.
    """
    global _qt_widgets, _qt_checked
    if _qt_checked:
        return _qt_widgets
    _qt_checked = True
    for name in _QT_WIDGET_MODULES:
        try:
            # Optional GUI stack. Any import failure leaves the unit tier runnable.
            _qt_widgets = __import__(name, fromlist=["QApplication", "QWidget"])
        except Exception:
            continue
        return _qt_widgets
    _qt_widgets = None
    return None


def _place_on_screen(widget: object, widgets: object) -> None:
    """Move a top-level widget onto the test screen before maximize.

    widget: the top-level window about to be shown.
    widgets: the imported Qt widgets module. QApplication lives on it.
    Screen choice reads TEST_SCREEN from the environment (blank means primary).
    """
    app = widgets.QApplication.instance()
    if app is None:
        return
    screens = list(app.screens())
    names = [screen.name() for screen in screens]
    primary = app.primaryScreen()
    primary_name = primary.name() if primary is not None else None
    chosen = prefer_screen_name(os.environ.get(TEST_SCREEN_ENV), names, primary_name)
    # The screen whose name matches the choice, or None when that name is absent.
    target = next((screen for screen in screens if screen.name() == chosen), None)
    if target is None or not hasattr(widget, "setScreen"):
        return
    widget.setScreen(target)


def _install_maximized_show(monkeypatch: pytest.MonkeyPatch, widgets: object) -> None:
    """Wrap QWidget.show so top-level windows maximize on the test screen.

    monkeypatch: restores the original show method after this test.
    widgets: the imported Qt widgets module. QWidget lives on it.
    """
    original_show = widgets.QWidget.show

    def _show(self, *args, **kwargs):  # noqa: ANN001 — Qt widget; the binding is optional
        # showMaximized can re-enter show. The id guard stops that loop.
        ident = id(self)
        top_level = bool(self.isWindow())
        if ident in _SHOWING or not should_maximize(windowed=False, is_window=top_level):
            return original_show(self, *args, **kwargs)
        _SHOWING.add(ident)
        try:
            _place_on_screen(self, widgets)
            return self.showMaximized()
        finally:
            _SHOWING.discard(ident)

    monkeypatch.setattr(widgets.QWidget, "show", _show)


def _close_top_level_widgets(widgets: object) -> None:
    """Close and delete top-level widgets this test left open.

    widgets: the imported Qt widgets module.
    No application means this test never opened a window.
    """
    app = widgets.QApplication.instance()
    if app is None:
        return
    for widget in list(app.topLevelWidgets()):
        widget.close()
        widget.deleteLater()
    app.processEvents()


@pytest.fixture(autouse=True)
def maximize_top_level_windows(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    """Show new top-level Qt windows maximized on one screen, then close them.

    Lesson: a window left open, or a screen that changes between machines,
    changes the next test's result. Maximize on one screen and close widgets here.

    request: this test. A windowed marker skips the maximize patch.
    monkeypatch: restores QT_QPA_PLATFORM and QWidget.show so they do not leak.

    Headless Linux (no DISPLAY and no WAYLAND_DISPLAY) selects the offscreen
    platform for this test only. Windows and macOS keep the native platform so
    a person can see the maximized window. Set QT_QPA_PLATFORM=offscreen to
    force headless on any OS. The fixture does not construct QApplication;
    the test does, after this fixture has set the platform.
    """
    widgets = _load_qt_widgets()
    if widgets is not None:
        if headless_platform_needed(os.environ, sys.platform):
            monkeypatch.setenv(QT_PLATFORM_ENV, OFFSCREEN_PLATFORM)
        if request.node.get_closest_marker("windowed") is None:
            _install_maximized_show(monkeypatch, widgets)
    yield
    if widgets is not None:
        _close_top_level_widgets(widgets)
