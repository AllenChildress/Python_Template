"""Promote a live PNG/JPEG into a tracked Change_Log thumbnail.

Runtime dumps stay gitignored (typical: data/Graphics/Screenshots/, including error_*).
Curated thumbs live under docs/changelog_shots/ so Preview and git keep them.

Usage:
    python scripts/promote_changelog_shot.py --tab main --source path.png
    python scripts/promote_changelog_shot.py --tab settings --source path.png --date 2026-08-13 --hint chrome

Prints the Change_Log **Shot:** HTML line to paste.

Sensitive views (PII, account numbers, money) require --allow-sensitive.
Pillow is used when installed; otherwise the file is copied as-is if it is already a JPEG.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOT_DIR = ROOT / "docs" / "changelog_shots"
MAX_WIDTH = 900
JPEG_QUALITY = 78

# Apps replace this list with their view slugs.
TAB_SLUGS = (
    "main",
    "settings",
    "log",
    "shell",
    "chart",
    "options",
    "analytics",
    "positions",
    "history",
    "data",
    "project",
)
SENSITIVE_TABS = frozenset({"positions", "history"})


def changelog_shot_filename(day: datetime | date, tab: str, hint: str = "") -> str:
    extra = f"_{hint.strip().lower().replace(' ', '_')}" if hint.strip() else ""
    extra = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in extra)
    stamp = day.strftime("%Y-%m-%d") if hasattr(day, "strftime") else str(day)
    return f"{stamp}_{tab}{extra}.jpg"


def changelog_shot_markdown(rel_name: str, alt: str) -> str:
    return f'- **Shot:** <img src="changelog_shots/{rel_name}" width="360" alt="{alt}">'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a PNG to docs/changelog_shots/")
    parser.add_argument("--tab", required=True, choices=TAB_SLUGS, help="Modified view / tab")
    parser.add_argument("--source", required=True, type=Path, help="Source PNG/JPG")
    parser.add_argument("--date", default="", help="YYYY-MM-DD (default today)")
    parser.add_argument("--hint", default="", help="Optional extra slug")
    parser.add_argument(
        "--allow-sensitive",
        "--allow-account",
        dest="allow_sensitive",
        action="store_true",
        help="Required to promote positions/history (or other SENSITIVE_TABS).",
    )
    return parser.parse_args()


def promote(source: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        if source.suffix.lower() not in {".jpg", ".jpeg"}:
            raise SystemExit(
                "FAIL: Pillow is required to convert PNG → JPEG. "
                "pip install pillow  (or pass an existing .jpg)"
            )
        shutil.copy2(source, dest)
        return dest

    image = Image.open(source).convert("RGB")
    if image.width > MAX_WIDTH:
        height = max(1, round(image.height * (MAX_WIDTH / image.width)))
        image = image.resize((MAX_WIDTH, height), Image.Resampling.LANCZOS)
    image.save(dest, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return dest


def main() -> int:
    args = parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    if not source.is_file():
        print(f"FAIL: missing source {source}")
        return 1
    if args.tab in SENSITIVE_TABS and not args.allow_sensitive:
        print(
            "FAIL: this tab is in SENSITIVE_TABS. "
            "Pass --allow-sensitive after privacy mode or a crop."
        )
        return 2
    day = date.fromisoformat(args.date) if args.date else date.today()
    name = changelog_shot_filename(day, args.tab, args.hint)
    dest = SHOT_DIR / name
    promote(source, dest)
    alt = f"{day.isoformat()} {args.tab} {args.hint}".strip()
    print(f"Wrote {dest.relative_to(ROOT)} ({dest.stat().st_size} bytes)")
    print(changelog_shot_markdown(name, alt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
