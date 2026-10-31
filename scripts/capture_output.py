"""Gitignored folders for smoke captures.

Callers pass the repository root and the environment. A machine-specific
folder belongs in CAPTURE_OUTPUT_DIR or CAPTURE_TEXT_DIR, not in this file.
"""

from __future__ import annotations

from collections.abc import Mapping  # environ passed by the script or a test
from pathlib import Path  # repo root and relative capture folders

# Repo-relative defaults. .gitignore covers both. Override with the env keys.
GUI_CAPTURE_ENV = "CAPTURE_OUTPUT_DIR"
TEXT_CAPTURE_ENV = "CAPTURE_TEXT_DIR"
GUI_CAPTURE_DEFAULT = Path("data") / "Graphics" / "Screenshots"
TEXT_CAPTURE_DEFAULT = Path("data") / "ConsoleCaptures"


def capture_dir(
    root: Path,
    environ: Mapping[str, str],
    env_key: str,
    default: Path,
) -> Path:
    """Resolve one gitignored capture directory.

    root: repository root, derived by the caller from this file's location.
    environ: process environment, or a test double. Read env_key from it.
    env_key: name of the override variable. Blank or missing means default.
    default: path relative to root when the override is unset.
    An absolute override is used as given. A relative override joins root.
    """
    raw = (environ.get(env_key) or "").strip()
    if not raw:
        return (root / default).resolve()
    chosen = Path(raw)
    if chosen.is_absolute():
        return chosen
    return (root / chosen).resolve()


def gui_capture_dir(root: Path, environ: Mapping[str, str]) -> Path:
    """Folder for GUI PNG captures.

    root: repository root.
    environ: process environment. CAPTURE_OUTPUT_DIR overrides the default.
    """
    return capture_dir(root, environ, GUI_CAPTURE_ENV, GUI_CAPTURE_DEFAULT)


def text_capture_dir(root: Path, environ: Mapping[str, str]) -> Path:
    """Folder for console and TUI text captures.

    root: repository root.
    environ: process environment. CAPTURE_TEXT_DIR overrides the default.
    """
    return capture_dir(root, environ, TEXT_CAPTURE_ENV, TEXT_CAPTURE_DEFAULT)
