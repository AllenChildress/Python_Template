# Lessons learned

Durable scars. Prefer **short rules** over novels.

## Grok multi-session

- **Grok managed worktrees, short-lived branches (2026-10-01).** Requires Grok Build **1.0.42 or newer**. One writer, short task: stay in the primary checkout; no worktree; no branch until the diff is worth keeping. Second writer or a long task: Grok managed worktree, detached, off current `main` (`grok -w --ref main` / `grok worktree create`). **Never** edit the primary checkout while another Grok session is editing. A Grok worktree does not create a branch. Do not `git worktree add -b wip/<topic>`.
- **VS Code purple pick is for the second writer.** Recommended only in that case; label it a detached Grok worktree. One writer, short task: stay. After a worktree is created, **stop editing the primary tree**.
- **Mandatory `wip/` worktree (2026-08-25) is superseded.** Isolation is the Grok worktree folder, not a long-lived `wip/` branch. Land: `git switch main && git pull --ff-only`, then branch only if the diff is worth keeping, squash-merge, delete local and remote branches, `grok worktree rm <id>`.
- **Missing locals (2026-10-28).** A detached or second checkout copies the commit, not `.env`, tokens, or caches. With no `.env`, startup can silently use `.env.example` paths, open the wrong database, and split data into another folder. Copy `.env` into every checkout. Use absolute data and log paths. Show and log the resolved paths at startup, before asking anyone to run the app.
- **Two independently opened chats cannot DM each other.** The human is the bus. Durable handoff is git.
- **`checkout -b` still moves this folder.** Two chats here share one checkout. Do not `checkout -b` in the primary tree to “make room.”
- **One-folder lock (2026-08-17) is superseded** for a **second writer**. One writer, short task still stays in the primary folder.
- **Database changes are single-threaded.** Copied `.env` points every worktree at the same database. Before DDL / migrations: `git worktree list` — this session must be the only topic worktree. If another exists, stop. Idle leftover folders still count until removed.
- **Finish pass.** `grok worktree list`, `git worktree list`, `git branch -vv`. A branch with no worktree and no open PR is trash.

## Tests (portable)

- **State leak (2026-10-23).** Anything one test leaves behind that changes another test's result. Symptom: the test passes alone and fails in the full suite, or the other way around. Glossary **State leak**. Rules: PROCESS § Tests and [tests/README.md](../tests/README.md).
- **No hardcoded POSIX paths (2026-10-28).** A literal such as `/opt/…` passes on Linux and fails on Windows, because `resolve()` adds a drive letter. Build test paths from `tmp_path` and compare `resolve()` on both sides. PROCESS § Tests already writes files under `tmp_path`.
- **We do not push broken code (2026-10-16).** Stock_Data PR #188 landed Chart work while `--tier ui` was still red. The agent reported FAIL, called it SHORTFALL, and squash-merged. Honesty without a stop is not a gate.
- Path: **fix it this session**, or **stop and discuss with the human** so it can be fixed. Proven pre-existing is not this session’s regression — same turn **identify who caused it** (commit/author/session) and **get them to fix it**, **or this session takes ownership and fixes it**. Parking it as SHORTFALL-only is not allowed.
- Lock: PROCESS § Tests, Coding_Standards Warnings, AGENTS checklist **Known pytest FAIL?**

## General (portable)

- **Dense one-liners (2026-10-01).** Powerful clean one-liners are welcome. McCabe CC will not flag them (a filtered comprehension is still CC 1). Put a one-line English comment that names the **outcome**. Split only when that comment cannot be straightforward. Coding_Standards **Dense one-liners (explain first)**.
- Incomplete renames across UI stacks thrash more than file renames on disk — finish one vocabulary (e.g. page_key) in one series.
- Wide Markdown tables can break Preview; prefer vertical entries for long logs.
- Agent context: open only the docs the task needs, not the whole tree.
- SQL as app string literals ages badly (one-liners too) — put statements in `.sql` files and load them by name (Coding_Standards).
- Prefer names that match the job (`db_report`, inventory). “Health” and similar borrowed words confuse readers when the domain is not medical.
- **Why Coding_Standards is long:** many entries exist because **Grok Build did not do them by default**, and other LLMs often will not either. Treat the standards file as the forced checklist for agents — do not assume the model already “knows” Rule of Three, SQL-in-files, 500-line caps, or cohesion pairs.

## Domain / product

_(Move product- or domain-specific lessons here or into the app repo — keep this kit portable.)_

## Environment

- **QTimer belongs on the window thread (2026-09-30).** A `QTimer` is a window object, like a widget. Only the GUI / window thread may construct one. A worker must not call `QTimer(...)` or parent a timer to a widget on another thread. Marshal with a queued helper (`ui_single_shot` or equivalent). Do not fall back to running the GUI callback on the worker if marshal fails. Log: `Cannot create children for a parent that is in a different thread` (a logger that eats the words “for a” can look like ticker “A”).
- **The window thread does not search data (2026-09-30).** Date searches, hole scans, and store/SQL on the paint / mouse thread freeze the cursor until the function returns. Workers load domain objects and DataFrames; the window only applies them. MVC: database / domain / view — a database change must not force UI edits.
- **Same hit region, and log the miss (2026-10-28).** Hover and click share one hit region. A hover on the whole column and a click only on the thin bar looks dead, and a silent handler leaves no trace. Log every UI action, including a miss (`double-click … / miss`), so the log alone shows where it stopped.

## Windows executable packaging (PyInstaller)

- **Packed paths are absolute (2026-10-28).** PyInstaller resolves relative `datas`, `--add-data`, and icon paths against the spec or work folder (`build\`), not the repo root. Build every packed-file path as an absolute path from the repo root (for example `$PSScriptRoot\..`).
- **One Qt binding in the build interpreter (2026-10-28).** PyInstaller aborts when more than one Qt binding (PyQt5, PySide6, and the rest) is installed. Exclude every binding the app does not import. Pin `QT_API` and the matplotlib backend.
- **Build from a clean venv (2026-10-28).** A big global env (Anaconda) makes PyInstaller import everything during “Looking for dynamic libraries”. pandas pulls in SciPy, and `pkg_resources` pulls in torch, so one build can stall for many minutes. Build from a clean, gitignored venv that holds only the requirements plus PyInstaller. Keep a spec excludes list (torch, tensorflow, scipy, matplotlib, IPython, and the like) as a backstop. Print the exe size at the end.
- **Scrub the conda PATH (2026-10-28).** A venv created from Anaconda’s Python still picks up Anaconda’s `Library\bin` DLLs from PATH. The result is `DLL load failed … The specified procedure could not be found` on `PySide6.QtCore`. For the build, scrub PATH (anaconda, miniconda, `Library\bin`, conda envs, user-site Scripts) and clear `QT_PLUGIN_PATH`, `PYTHONPATH`, `PYTHONHOME`, and `CONDA_*`. Preflight `import PySide6.QtCore` with a clear message. If that still fails, fall back to a python.org interpreter.
- **PySide6 Essentials, not the metapackage (2026-10-28).** The PySide6 metapackage drags in WebEngine, Pdf, and Addons, sometimes as mismatched builds. When the app only uses QtCore, QtGui, and QtWidgets, install `PySide6_Essentials` pinned to a matching `shiboken6`.
- **The user’s Windows machine is the real exe test (2026-10-28).** A Linux cloud VM cannot produce or run a Windows executable. Say that plainly. Give one paste-ready command that runs the tests, the build, and the launch, and stops on the first failure.
- **Tray icons are cached and smoothed (2026-10-28).** Windows caches tray and taskbar icons by process (`python.exe`). Qt smooth-scales a small icon. Set an explicit AppUserModelID and paint each icon size exactly.
- **Long-run leak check.** Before packaging an app that stays up for days or weeks, follow [PROCESS § Executable production](PROCESS.md#executable-production). That section is the gate. Do not restate it here.
