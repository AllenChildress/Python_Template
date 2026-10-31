# Scripts (staff kit)

Portable helpers. App repos add product-specific scripts here or under `scripts/testing/`.

| Script | Role |
|--------|------|
| [promote_changelog_shot.py](promote_changelog_shot.py) | Resize one PNG/JPEG into `docs/changelog_shots/` and print the Change_Log **Shot:** line |
| [capture_changelog_tabs.py](capture_changelog_tabs.py) | **GUI smoke capture.** Bind it so one command writes PNGs under the gitignored screenshot folder. Promote one of those with the script above when a Change_Log thumb is due. |
| [capture_console_text.py](capture_console_text.py) | **Console / TUI smoke capture.** Bind it so one command writes stdout and stderr under the gitignored text folder. No thumbnail step. |
| [capture_output.py](capture_output.py) | Resolves those folders from `CAPTURE_OUTPUT_DIR` / `CAPTURE_TEXT_DIR` |
| [score_cc.py](score_cc.py) | McCabe cyclomatic complexity on functions (**≤ 10** target, **> 15** too high) |
| [run_tiers.py](run_tiers.py) | Pytest tiers in order. Inputs: tier paths. Exit 5 (no tests collected) counts as pass. Any other nonzero stops and names that tier. |

See [docs/PROCESS.md](../docs/PROCESS.md) § Screenshots and § Cyclomatic complexity.
