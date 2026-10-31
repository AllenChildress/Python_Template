"""Console / TUI smoke capture. One command writes reviewable text files.

This kit has no program to run. On adoption, bind the body so it runs the
app (or its main screens and commands) and saves stdout and stderr under
the gitignored text folder. Exit 0 when a file was written.

Change_Log thumbnails are a GUI step. Text captures stay in the gitignored
folder for review and diff. There is no promote step.

Run from the repo root, with the project's interpreter:

    python scripts/capture_console_text.py -- python -m your_app --help
"""

from __future__ import annotations

import os  # CAPTURE_TEXT_DIR, via text_capture_dir
import sys  # argv: tokens after -- are the program and its arguments
from pathlib import Path  # this file's location; the repo root is its parent

from capture_output import text_capture_dir  # gitignored folder for the text files

ROOT = Path(__file__).resolve().parents[1]


def command_after_double_dash(argv: list[str]) -> list[str]:
    """Return the program and arguments the capture should run.

    argv: the full argument list, including the script name at index 0.
    Tokens after the first lone ``--`` are the command. No ``--`` means
    an empty command (the script is not bound to a program yet).
    """
    if "--" not in argv:
        return []
    return argv[argv.index("--") + 1 :]


def main(argv: list[str] | None = None) -> int:
    """Print the capture folder and exit 2 until an app binds a real run.

    argv: the argument list. None uses sys.argv. The command is everything
    after ``--`` (see command_after_double_dash). The output directory comes
    from text_capture_dir: root is this repo, environ is os.environ, and
    CAPTURE_TEXT_DIR overrides the default folder.
    """
    args = list(sys.argv if argv is None else argv)
    command = command_after_double_dash(args)
    folder = text_capture_dir(ROOT, os.environ)
    shown = " ".join(command) if command else "(pass the program after --)"
    print(
        "STUB: bind scripts/capture_console_text.py so this command runs the "
        "program and writes stdout and stderr into the capture folder.\n"
        f"Command: {shown}\n"
        f"Capture folder: {folder}\n"
        "See tests/README.md § Capture on adoption."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
