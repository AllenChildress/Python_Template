"""GUI smoke capture. One command writes PNGs, then you may promote one thumb.

This kit has no window. On adoption, bind this file so it:

1. Launches the app. Headless runs set QT_QPA_PLATFORM=offscreen first.
2. Waits until the main-window paint is real.
3. Grabs the main window and each tab to PNG files in the gitignored
   capture folder (scripts/capture_output.py, CAPTURE_OUTPUT_DIR).
4. Closes the widgets and quits.

Change_Log thumbs are a second step. Pick one PNG and run
scripts/promote_changelog_shot.py --tab <slug> --source <that png>.
Tracked thumbs live in docs/changelog_shots/. Raw PNGs stay gitignored.
Do not promote error dumps. Sensitive views need --allow-sensitive.

Console and TUI apps use scripts/capture_console_text.py instead.

Run from the repo root, with the project's interpreter:

    python scripts/capture_changelog_tabs.py
"""

from __future__ import annotations

import os  # CAPTURE_OUTPUT_DIR, via gui_capture_dir
from pathlib import Path  # this file's location; the repo root is its parent

from capture_output import gui_capture_dir  # gitignored folder for the PNG files

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Print the capture folder and exit 2 until an app binds a real window.

    No parameters. The folder comes from gui_capture_dir.
    root: the repository root (parent of the scripts directory).
    environ: os.environ. CAPTURE_OUTPUT_DIR overrides the default folder.
    """
    folder = gui_capture_dir(ROOT, os.environ)
    print(
        "STUB: bind scripts/capture_changelog_tabs.py to your window, grab "
        "each view into the capture folder, then call "
        "scripts/promote_changelog_shot.py for the Change_Log thumb.\n"
        f"Capture folder: {folder}\n"
        "See docs/PROCESS.md § Change_Log screenshots and tests/README.md."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
