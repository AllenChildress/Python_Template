# Change Log

All notable changes to **YOUR_APP** are recorded here.

Each entry: **date**, optional time, **files**, short title, then **Why** / **What** / **Benefit**.

Prefer a **vertical list** (not a wide table) so Markdown Preview stays readable.

| Field | Role |
|-------|------|
| **Files** | Paths or short module names touched |
| **Why** | Problem or product need |
| **What** | What shipped (concrete) |
| **Benefit** | Short user/dev outcome |
| **Shot** | Required when a **view or chrome paint** changed — HTML thumbnail from [changelog_shots/](changelog_shots/) (see PROCESS § Screenshots) |

**Shot:** use the HTML thumbnail `scripts/promote_changelog_shot.py` prints (width 360). Do not embed full-size PNGs or error dumps.

### UI progression (curated)

Newest real UI steps, oldest last. Same image may also appear on the dated **Shot:** row — that is intentional.

<!-- Add promoted thumbs here, newest first. Example:
- YYYY-MM-DD Main window  
  <img src="changelog_shots/YYYY-MM-DD_main.jpg" width="360" alt="YYYY-MM-DD main">
-->

## Benefit vocabulary (optional)

- Bug fix  
- Save user time / workflow speed  
- Improve accuracy / data correctness  
- Performance increase  
- Reduce technical debt  
- Improve maintainability  
- UX clarity  
- Reliability / stability  
- Security  
- Tests / regression prevention  
- New feature  
- Improve code hygiene / documentation  

---

## Entries (newest first)

### 2026-10-30 — Agent runs the suite and reads the saved file

- **Files:** `docs/PROCESS.md`, `AGENTS.md`, `tests/README.md`, `.gitignore`
- **Why:** The human was pasting the pytest summary back. The agent can run the suite on the human's machine and read the file.
- **What:** PROCESS § Saved test output. The agent runs the four-tier chain, writes `logs\last_test_run.txt` and a dated copy (`PR<n>`, `main`, or the branch name), hashes `.env`, and reports **FAIL** or pass, counts per tier, which tier stopped the run, the `.env` line, and each failure by file and name. Dated copies older than 2 days are deleted. `logs/` is gitignored. The human does the in-app checks.
- **Benefit:** Save user time / workflow speed

### 2026-10-28 — Windows exe packaging and UI-miss lessons

- **Files:** `docs/Lessons_Learned.md`
- **Why:** Packaging a Windows executable, a second checkout, and a dead double-click were scars in one app. The kit had no portable rule, so the next app would repeat them.
- **What:** Lessons_Learned gains a Windows executable packaging (PyInstaller) group: absolute packed paths, one Qt binding, a clean build venv, a scrubbed conda PATH, PySide6 Essentials, the user’s Windows machine as the real exe test, and exact tray icons. The long-run leak check cross-links PROCESS § Executable production. Tests build paths from `tmp_path`. A second checkout copies `.env`, uses absolute data and log paths, and logs them. Hover and click share a hit region, and every UI action including a miss is logged.
- **Benefit:** Improve code hygiene / documentation

### 2026-10-28 — Long-run leak check before an executable

- **Files:** `docs/PROCESS.md`, `AGENTS.md`
- **Why:** An app expected to run for days or weeks can leak memory that a short session never shows. That leak ships inside the executable.
- **What:** PROCESS § Executable production. Before packaging that app: review common leak sources (per-refresh UI objects, remade timers and signals, unpruned caches, re-reading growing files, unclosed DB/HTTP/socket/child-process handles, day-rollover state, unrotated logs). An accelerated soak under `running_under_tests()` skips real waits, runs thousands of refresh cycles and many simulated day rollovers in seconds, and fails if `tracemalloc` or object counts keep climbing. The running app logs RSS at DEBUG about once an hour.
- **Benefit:** Reliability / stability

### 2026-10-28 — PR flow: three open, then hold

- **Files:** `docs/PROCESS.md`, `AGENTS.md`, `tests/README.md`
- **Why:** PRs left open while newer merges land go stale and conflict.
- **What:** Allen's PR flow (adopted 2026-10-27), for any project from this template. WIP limit of 3: at three open untested PRs the assistant says `hold: 3 open` and starts no new PR. During a hold, new ideas go to `docs/ToDo.md` and ride in the next PR; only a real bug in a PR under test is added to that PR. Every test command names which PR merges first and ends with every open PR and what it is waiting on. A PR untested for 24 hours gets flagged (a nightly check is enough). No GitHub Actions.
- **Benefit:** Improve maintainability

### 2026-10-25 — Tier meanings, and an empty tier does not stop the chain

- **Files:** `docs/PROCESS.md`, `tests/README.md`, `AGENTS.md`, `docs/Glossary.md`, `docs/Coding_Standards.md`, `Project.md`, `tests/conftest.py`, `tests/smoke/`, `tests/integration/`, `scripts/run_tiers.py`, `scripts/README.md`, `tests/unit/test_run_tiers.py`
- **Why:** Smoke was only "the app boots." A real local service had been called integration. An empty tier made pytest exit 5 and stopped the kit's own chain.
- **What:** Unit is function in, outputs match. Smoke checks that key components work: the app boots and reaches the important places (external services, database, each core feature). If it fails, call the engineers before production users hit it. The old real-local-service meaning sits on smoke, and so does the adoption capture. Integration is the happy path from the start. Regression is the edge cases. `scripts/run_tiers.py` treats pytest exit 5 as pass and stops on any other nonzero code. `tests/smoke/` and `tests/integration/` are in the tree.
- **Benefit:** Tests / regression prevention

### 2026-10-25 — Test tiers run in order and stop on the first failure

- **Files:** `docs/PROCESS.md`, `tests/README.md`, `AGENTS.md`, `tests/conftest.py`, `tests/regression/`, `tests/unit/test_regression_marker.py`, `README.md`, `Project.md`, `docs/Coding_Standards.md`, `docs/Glossary.md`, `docs/Libraries.md`
- **Why:** The kit named unit, integration, and smoke, and did not say which to run first. A later tier could start after an earlier one had already failed.
- **What:** Run order is unit, then smoke, then integration, then regression. Stop before the next tier when one fails. Canaries stay a sniff list inside unit when CI is unfolded. No GitHub Actions and no testmon.
- **Benefit:** Tests / regression prevention

### 2026-10-23 — Agents write and maintain tests

- **Files:** `tests/README.md`, `docs/PROCESS.md`, `AGENTS.md`, `docs/Glossary.md`, `docs/Lessons_Learned.md`, `docs/Coding_Standards.md`, `docs/changelog_shots/README.md`, `Project.md`, `README.md`, `tests/conftest.py`, `tests/window_policy.py`, `tests/unit/test_window_policy.py`, `tests/unit/test_capture_output.py`, `scripts/capture_output.py`, `scripts/capture_changelog_tabs.py`, `scripts/capture_console_text.py`, `scripts/README.md`, `.gitignore`, `.env.example`
- **Why:** The kit had test folders and a red-test rule, and no how-to for writing tests. Adopting an app left agents without a smoke capture, and a test that passed alone could fail in the suite because leaked state had no name.
- **What:** Duty, tiers, isolation, GUI window fixture, and paste-ready run commands. Glossary defines state leak. On adoption, bind one capture script: GUI PNGs (`capture_changelog_tabs.py`, then promote one thumb) or console text (`capture_console_text.py`). CI, testmon, and canaries stay dormant.
- **Benefit:** Tests / regression prevention

### 2026-10-16 — Leave the code better than you found it

- **Files:** `docs/Taste.md`, `docs/Coding_Standards.md`, `AGENTS.md`
- **Why:** Truth, maintainability, performance, and reliability had no single umbrella. Knowingly landing worse code is how you lose the customer.
- **What:** Scout outdoor code: leave the place better than you found it. A slice ships when the tree is as good or better (bugs, speed, clutter, reliability). Scout Law is the character list. Always-on pointer in Coding_Standards; full text in Taste.
- **Benefit:** Improve code hygiene / documentation

### 2026-10-16 — Fix a red test or discuss it; do not push broken code

- **Files:** `docs/PROCESS.md`, `docs/Coding_Standards.md`, `AGENTS.md`, `docs/Taste.md`, `docs/Lessons_Learned.md`
- **Why:** Stock_Data PR #188 shipped a known `--tier ui` fail behind SHORTFALL. Honesty without a stop is not a gate. A pre-existing red still needs an owner this turn.
- **What:** We do not push broken code. Path: fix it this session or stop and discuss with the human. Proven pre-existing: name who caused it; they fix it or this session owns the fix.
- **Benefit:** Improve code hygiene / documentation

### 2026-10-07 — Do not hardcode paths, URLs, or file names

- **Files:** `docs/Coding_Standards.md`, `AGENTS.md`
- **Why:** A clone-folder guess only works on one PC. Allen does not authorize hardcoded paths, URLs, or file names.
- **What:** A priori lock: those values live in `.env` / config or are derived. Rule of Three “once is fine” does not cover them.
- **Benefit:** Improve code hygiene / documentation

### 2026-10-01 — Pin Grok 1.0.42 worktrees and vendor git skill

- **Files:** `.grok/skills/git-workflow-and-versioning/SKILL.md`, `AGENTS.md`, `README.md`, `docs/PROCESS.md`, `docs/skills/README.md`, `docs/Glossary.md`, `docs/Lessons_Learned.md`, `docs/Coding_Standards.md`
- **Why:** Git followed a mandatory `wip/` worktree. A second writer should use a Grok managed worktree, and the branch should die with the merge.
- **What:** Requires Grok Build 1.0.42 or newer. One writer, short task: primary checkout, no worktree, no branch until the diff is worth keeping. Second writer: `grok -w --ref main` / `grok worktree create` (detached). Vendored git skill unchanged; this kit’s worktree and branch-delete rules override it.
- **Benefit:** Improve code hygiene / documentation

### 2026-10-01 — Remove the specialist roster

- **Files:** `AGENTS.md`, `Project.md`, `README.md`, `docs/PROCESS.md`, `docs/Coding_Standards.md`, `docs/Lessons_Learned.md`, `docs/skills/README.md`, `docs/skills/General/Multi_Agent_Project_Setup.md` (deleted)
- **Why:** Hiring DBA, UI, and the other named roles added chat noise and did not improve the work. Replies still opened with `main:` because that instruction stayed in the kit.
- **What:** This session does the work. Replies start with the answer. The multi-agent playbook is deleted. Nested `AGENTS.md` files stay as folder reading lists. SQL still lives in `.sql` files. The short note to the human stays.
- **Benefit:** Improve code hygiene / documentation

### 2026-10-01 — Dense one-liners get a why-comment first

- **Files:** `docs/Coding_Standards.md`, Lessons
- **Why:** A filtered comprehension is still cyclomatic complexity 1, so the CC gate never asked for a comment. Powerful clean one-liners are welcome; unexplained ones are not.
- **What:** Rule **Dense one-liners (explain first)**. Comment the outcome. Split only when a straightforward comment cannot name the line.
- **Benefit:** Improve code hygiene / documentation

### 2026-09-30 — QTimer and data calls stay off the worker / window mix-up

- **Files:** `docs/Coding_Standards.md`, Lessons
- **Why:** Constructing `QTimer` on a worker (or parenting it to a window widget from that worker) logs a wrong-thread children warning. SQL on the window thread freezes the mouse.
- **What:** Only the window thread constructs `QTimer`; workers marshal. The window never issues a data call (MVC: database / domain / view).
- **Benefit:** Reliability / stability

### 2026-09-03 — Click-path tutorial stays current with UI

- **Files:** `docs/PROCESS.md`
- **Why:** Screenshot Change_Log thumbs are not a how-to-click guide. Apps that add `docs/tutorial/` need agents to update the matching page when chrome or user-visible backend changes.
- **What:** PROCESS screenshots: if `docs/tutorial/` exists, update the matching page in the same series as UI or backend-that-affects-UI work. Keep pages short.
- **Benefit:** Improve code hygiene / documentation

### 2026-09-03 — CI / pytest unfold stays dormant until a threshold

- **Files:** `docs/PROCESS.md`, `AGENTS.md`, `tests/README.md`, `Project.md`, Glossary
- **Why:** A new app should not inherit Stock_Data’s GitHub Actions, canaries, and pytest-testmon on day one. Those pay off only after a real suite exists.
- **What:** Default dormant. Unfold with **one** purple pick when ≥25 unit tests, a suite runner, or the human asks for CI. Recommended shape: canaries then unit; testmon `--impacted` local only; CI never uses `--impacted`.
- **Benefit:** Improve code hygiene / documentation

### 2026-09-03 — Purple multi-picks do not time out

- **Files:** `AGENTS.md`, `docs/PROCESS.md`
- **Why:** A timed-out pick looks declined and the agent keeps going in the wrong tree. The CLI default is 30 minutes; VS Code Grok Build also idles `session/prompt` at 30 minutes of silence.
- **What:** Lock CLI `[toolset.ask_user_question] timeout_enabled = false` (`~/.grok/config.toml` and `requirements.toml`). VS Code: `grok.acp.promptIdleTimeoutMs = 0`. Abort only if a pick **still** times out (old session / host bug).
- **Benefit:** Reliability / stability

### 2026-08-25 — Database changes are single-threaded across worktrees

- **Files:** `AGENTS.md`, `docs/PROCESS.md`, Lessons
- **Why:** Worktrees copy `.env`, so they share one database. Two sessions migrating, or one migrating while another runs the app, will collide.
- **What:** Before DDL / migrations, `git worktree list`. This session must be the **only topic worktree** (primary `main` checkout may remain). If another worktree is in play, stop and tell the human.
- **Benefit:** Reliability / stability

### 2026-08-25 — Parallel Grok sessions: worktree isolation

- **Files:** `AGENTS.md`, `docs/PROCESS.md`, Glossary, Lessons, `docs/Coding_Standards.md`
- **Why:** Two Grok chats in the primary folder share one checkout. `checkout -b` in the second chat moves the first and mixes uncommitted files. VS Code Grok Build has no `--worktree` launch switch.
- **What:** Concurrent / long-running sessions **must** start in a dedicated worktree + unique branch. **VS Code:** purple worktree pick before the first edit (Recommended `New worktree wip/<topic>` + Stay in this tree); create from `main`, copy locals, stop editing the primary tree. **CLI/TUI:** `grok --worktree=<name> --ref main`. File-touching subagents: `isolation: worktree`. Finish: push + PR (or merge) + remove the worktree. Permission timeout aborts the tree. The 2026-08-17 one-folder lock is reversed.
- **Benefit:** Reliability / stability

### 2026-08-20 — Table columns autosize then stay resizable

- **Files:** `docs/Coding_Standards.md`
- **Why:** Desktop tables that lock column widths fight the mouse.
- **What:** UI standard: autosize columns to contents on first paint, then leave them user-resizable. Stretch at most the last column. Icon/checkbox columns may stay fixed.
- **Benefit:** UX clarity

### 2026-08-16 — Session wrap-up returns the shared folder to main

- **Files:** `AGENTS.md`, `docs/PROCESS.md`, `docs/Lessons_Learned.md`, `docs/Glossary.md`
- **Why:** `git worktree add` without a start-point inherits this folder’s HEAD. Pushing a topic branch does not move any folder back to `main`.
- **What:** Always pass `main` to `worktree add`. After a **This folder** session, `git checkout main` (checkout ≠ merge). PROCESS wrap-up table.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-17 — One folder; no default worktrees

- **Files:** `docs/PROCESS.md`, `docs/Lessons_Learned.md`
- **Why:** Sibling worktrees made a mess. Human lock: stay in the project folder.
- **What:** New session = `checkout -b` here. `git worktree add` only if asked.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-15 — Lessons: Grok multi-session

- **Files:** `docs/Lessons_Learned.md`
- **Why:** A “harmless” second chat that only `checkout -b` in the same folder can mix WIP and block a push. Two chats also cannot DM each other.
- **What:** New **Grok multi-session** category: branch ≠ folder, no inter-session backchannel, sibling worktree then open the chat there, `git worktree remove` when done.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-15 — New session = branch + sibling folder

- **Files:** `AGENTS.md`, `docs/PROCESS.md`, `docs/Lessons_Learned.md`, `docs/Glossary.md`
- **Why:** A branch name is not isolation. `checkout -b` in the shared project folder moves every chat using that folder onto the new branch and mixes uncommitted files.
- **What:** Default is `git worktree add ..\<RepoName>_<topic> -b wip/<topic>` and open the new chat **there**. Same-folder `checkout -b` is an explicit exception with a loud warning.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-14 — New chat session owns a topic branch

- **Files:** `AGENTS.md`
- **Why:** Parallel chats on `main` mix hunks. Spawned specialists must not each grow a branch.
- **What:** Session start: purple multi-pick for `wip/<topic>` (Recommended + Stay on current branch + built-in Other) before the first edit. Subagents stay on the parent branch. Warn if other WIP would ride along; prefer a worktree when two chats share a folder.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-13 — Change_Log screenshot thumbs (portable)

- **Files:** `docs/PROCESS.md`, `docs/Change_Log.md`, `AGENTS.md`, `scripts/promote_changelog_shot.py`, `scripts/capture_changelog_tabs.py`, `docs/changelog_shots/`, `tests/unit/test_promote_changelog_shot.py`
- **Why:** User-visible UI changes need a tracked progression, not only prose. Error dumps must stay out of git.
- **What:** PROCESS + Change_Log **Shot:** rule; promote script writes `docs/changelog_shots/*.jpg`; capture script is an app-bound stub. Sensitive views require `--allow-sensitive`.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-10 — Rule of Three for literals; SQL one-liners; standards why

- **Files:** Coding_Standards.md, Lessons_Learned.md
- **Why:** Agents skip literal centralization and leave one-liner SQL in source; kit readers need to know standards are forced checklist items.
- **What:** Rule of Three table (fourth copy → nearest constant); SQL-in-files includes one-liners; loader safety + INFO load log called out. Lessons: Coding_Standards entries exist because Grok Build (and other LLMs) don’t apply them by default.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-10 — SQL lives in files; cohesion pairs; process/DBA ownership

- **Files:** Coding_Standards.md, PROCESS.md, Database.md, AGENTS.md
- **Why:** Query text buried in app string literals blocks DBA review and duplicates migration discipline; portable kit should require the same fence as mature apps.
- **What:** Hard rule — multi-line SQL in `.sql` (or migration) files; DBA/schema lane owns statement text; app loads/runs. Cohesion pairs (SQL + loader). PROCESS migrations + Database wire steps aligned. Naming note: prefer inventory/report names over overloaded “health.”
- **Benefit:** Improve maintainability / Reduce technical debt / Improve code hygiene / documentation

### 2026-08-09 — Taste: Dijkstra / Northrop quotes

- **Files:** docs/Taste.md
- **Why:** Anchor kit judgment in classic engineering tenets, not fashion.
- **What:** Prefixed Taste.md with Dijkstra coding quotes (lines spent, simplicity, testing limits, abstraction, humility) and Jack Northrop’s efficient-and-beautiful line.
- **Benefit:** Improve code hygiene / documentation

### 2026-08-09 — Domain-neutral kit; setup links; light solo practices

- **Files:** README.md, Project.md, Database.md, Libraries.md, PROCESS.md, Glossary.md, Taste.md, Coding_Standards.md, AGENTS.md, skills READMEs, Lessons_Learned.md, .vscode/extensions.json
- **Why:** Template is a generic robust-app framework; product-domain examples and missing install links hurt portability.
- **What:** Removed Stock_Data / trading / broker-flavored wording; added Environment setup (Grok Build, Postgres, Python, VS Code extensions); lightweight solo/small-team practices; recommended extensions file.
- **Benefit:** Improve code hygiene / documentation; UX clarity for onboarding

### 2026-08-08 — Libraries + Database stubs; hard 500-line rule

- **Files:** Libraries.md, Database.md, Glossary.md, Coding_Standards.md, Project.md, README.md
- **Why:** Kit needed library menu, Postgres guidance, and absolute module-size rule.
- **What:** Libraries + Database decision tree (Postgres vs SQLite vs Timescale); Glossary library table; **500-line hard cap** (300 soft target); demo share caution for sensitive screenshots.
- **Benefit:** Improve code hygiene / documentation

### YYYY-MM-DD — Staff kit bootstrap

- **Files:** AGENTS.md, docs/*, Project.md, tests/README.md
- **Why:** Establish portable process for agents and humans.
- **What:** Copied LLM_Project_Template staff kit; filled intake placeholders as needed.
- **Benefit:** Improve code hygiene / documentation
