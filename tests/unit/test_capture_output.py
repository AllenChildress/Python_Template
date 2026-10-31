"""Smoke-capture folders and the console command tail. No GUI, no subprocess."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from capture_changelog_tabs import main as gui_capture_main  # noqa: E402  GUI stub exit
from capture_console_text import (  # noqa: E402  command tail and console stub exit
    command_after_double_dash,
    main as console_capture_main,
)
from capture_output import (  # noqa: E402
    GUI_CAPTURE_DEFAULT,
    TEXT_CAPTURE_DEFAULT,
    capture_dir,
    gui_capture_dir,
    text_capture_dir,
)


def test_missing_override_uses_the_relative_default(tmp_path: Path) -> None:
    """root: a stand-in repo. environ is empty, so default is used.

    env_key: the override name. default: the relative folder the caller asked for.
    """
    default = Path("data") / "Graphics" / "Screenshots"
    found = capture_dir(tmp_path, {}, "CAPTURE_OUTPUT_DIR", default)
    assert found == (tmp_path / default).resolve()


def test_blank_override_uses_the_relative_default(tmp_path: Path) -> None:
    """environ CAPTURE_OUTPUT_DIR is whitespace, which is the same as unset."""
    found = gui_capture_dir(tmp_path, {"CAPTURE_OUTPUT_DIR": "  "})
    assert found == (tmp_path / GUI_CAPTURE_DEFAULT).resolve()


def test_relative_override_joins_the_repo_root(tmp_path: Path) -> None:
    """environ CAPTURE_OUTPUT_DIR: a relative folder. root: the repo to join it to."""
    found = gui_capture_dir(tmp_path, {"CAPTURE_OUTPUT_DIR": "var/shots"})
    assert found == (tmp_path / "var" / "shots").resolve()


def test_absolute_override_is_used_as_given(tmp_path: Path) -> None:
    """environ CAPTURE_TEXT_DIR: an absolute folder. root is not prefixed."""
    absolute = tmp_path / "elsewhere"
    found = text_capture_dir(tmp_path, {"CAPTURE_TEXT_DIR": str(absolute)})
    assert found == absolute


def test_text_default_is_the_console_folder(tmp_path: Path) -> None:
    """environ is empty. root: the repo. The text default stays under that root."""
    found = text_capture_dir(tmp_path, {})
    assert found == (tmp_path / TEXT_CAPTURE_DEFAULT).resolve()


def test_command_tail_is_empty_without_a_separator() -> None:
    """argv: script name only. No -- means the capture is not bound to a program."""
    assert command_after_double_dash(["capture_console_text.py"]) == []


def test_command_tail_keeps_the_program_and_its_arguments() -> None:
    """argv: tokens after -- are the program and the arguments it should receive."""
    argv = ["capture_console_text.py", "--", "python", "-m", "your_app", "--help"]
    assert command_after_double_dash(argv) == ["python", "-m", "your_app", "--help"]


def test_console_stub_exits_until_an_app_binds_it() -> None:
    """argv: a program after --. This kit has nothing to run, so the stub exits 2."""
    code = console_capture_main(["capture_console_text.py", "--", "python", "-m", "your_app"])
    assert code == 2


def test_gui_stub_exits_until_an_app_binds_it() -> None:
    """No parameters. This kit has no window, so the stub exits 2."""
    assert gui_capture_main() == 2
