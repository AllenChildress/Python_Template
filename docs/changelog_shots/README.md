# Change_Log thumbnails

Tracked JPEG thumbs for [Change_Log.md](../Change_Log.md). Runtime dumps (including `error_*`) stay gitignored (typical: `data/Graphics/Screenshots/`).

GUI smoke capture writes those raw PNGs (`scripts/capture_changelog_tabs.py`). This folder receives only the one PNG you promote. Console captures (`scripts/capture_console_text.py`) have no thumb.

```powershell
python scripts/promote_changelog_shot.py --tab main --source "data/Graphics/Screenshots\<file>.png"
```

See [PROCESS.md](../PROCESS.md) § Screenshots.
