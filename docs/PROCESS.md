# Process (portable)

How humans and agents work on **any** project that uses this staff kit.

## Principles

1. **Outcome-level work** — design, implement, smoke, document without re-teaching process each time.
2. **Docs with the code** — same change series as behavior.
3. **When a session finishes:** `git switch main && git pull --ff-only`. If the diff is worth keeping, branch off that `main`, commit, squash-merge, delete the local branch and the remote branch. Then `grok worktree rm <id>` if this session used a managed worktree. Do not delete the primary checkout.
4. **Three open PRs, then hold** — [§ PR flow](#pr-flow).
5. **Short answers** to humans; completeness is in files and tests, not essay chat.

## Change_Log

For user-visible behavior: add a row with **Why** / **What** / **Benefit**.  
Prefer a vertical list (heading + bullets) if wide tables break your preview tool.

### Screenshots (each push that paints a view)

Goal: a visible **progression** of the UI, not a dump of error captures.

**When required:** the change altered what a user sees (window, tab, pane, chrome). Docs-only, schema-only, and headless work skip this.

**Same series as the code:**

1. Run the app (or a smoke shell if chrome-only).
2. Open **each modified view**. Wait until paint is real — not a spinner or blank pane.
3. Capture the window. Raw dumps go to a **gitignored** folder (typical: `data/Graphics/Screenshots/`). On adoption, bind `scripts/capture_changelog_tabs.py` so this grab is one command (Tests § Capture on adoption). Console and TUI apps write text with `scripts/capture_console_text.py` instead.
4. Promote a tracked JPEG thumb:
   ```powershell
   python scripts/promote_changelog_shot.py --tab main --source "data/Graphics/Screenshots/<file>.png"
   ```
   Replace `--tab` slugs with your app’s views (`main`, `settings`, `log`, `shell`, …).
5. Paste the printed `- **Shot:** <img …>` line on that Change_Log entry. Add the thumb to the **UI progression** strip at the top of Change_Log when it is a real step (new view, new overlay, new layout).
6. **Do not** promote `error_*` / `*_fail_*` dumps. Those stay local diagnostics.
7. Views that show **PII, account numbers, or money** need `--allow-sensitive` (privacy mode or crop first). Prefer non-sensitive views for the public strip.

Thumbs live in `docs/changelog_shots/` (tracked, JPEG, max width 900). Runtime PNGs stay gitignored.

If the app keeps a **click-path tutorial** (`docs/tutorial/`), update the matching page in the **same series** as a UI change or a backend change that alters what the user clicks or sees. Skip when there is no user-visible click/paint change. Keep those pages short (click → see → one thumb), not a second feature list.

Apps with a desktop shell should also keep a `scripts/capture_changelog_tabs.py` that boots the UI, waits for paint, and grabs each requested tab. The copy in this kit is a **stub** — bind it to your window.

## ToDo

- Open work in backlog columns.
- Finished items → **Done ✓** (or remove from open and record in Change_Log if user-visible).
- Do not leave stale checked items in “open” forever.
- While [§ PR flow](#pr-flow) is at `hold: 3 open`, new ideas land here and ride in the next PR. Do not start that work.

## Lessons_Learned

Non-obvious fixes, environmental traps, “never do X again.” Prefer durable rules over novel-length narratives.

## Commits

- Clear subject (what/why in one line).
- Optional body for multi-file stories.
- Optional trailer: `Assisted-by: Grok Build` (or your tool name).
- PowerShell-safe: write message to a file, `git commit -F …` (avoid nested quotes).

## Tests

Every new feature ships with a test. Every bug fix ships with a test that **fails first** because it reproduces the bug; the fix turns it green. When an agent edits code that has no test, it adds at least a **characterization test** (pin what the code does today) in the same change. Worked commands and copy-paste patterns: [tests/README.md](../tests/README.md).

**Adopting an existing codebase.** The first testing task is unit tests for the core logic, a smoke check that key components work, and the capture script on that smoke tier (below). Later changes grow the suite.

| Tier | When |
|------|------|
| **unit** | Supply inputs to a function and verify the outputs still match. No database, no network, no real window. |
| **smoke** | Key components work. The app boots and reaches the important places: external services (for example brokers or APIs), the database, and each core feature doing its core thing (for example charts, history, positions). If it fails, call the engineers before production users hit it. A real local service belongs here (this used to be called integration). Skip with a reason when a service is down. |
| **integration** | Run the whole thing from the start through key parts. Generally the happy path. |
| **regression** | The edge cases. |

A new behavior gets a unit test unless the only risk is the happy path from startup.

### Run order (fail-fast)

Run the tiers in this order: **unit**, **smoke**, **integration**, **regression**. If any test in a tier fails, stop before the next tier and say which tier stopped the run.

Pytest exit **5** (no tests collected) counts as a pass. Any other nonzero code stops the chain. [scripts/run_tiers.py](../scripts/run_tiers.py) does that. Its inputs are the tier paths, in order. It uses the interpreter that launches it.

```bash
.venv/bin/python scripts/run_tiers.py tests/unit tests/smoke tests/integration tests/regression
```

```powershell
.\.venv\Scripts\python.exe scripts\run_tiers.py tests/unit tests/smoke tests/integration tests/regression
```

### Isolation (no leaked state)

**Leaked state** is anything one test leaves behind that changes another test's result. Glossary: [state leak](Glossary.md). Symptom: a test passes alone and fails in the full suite, or the other way around.

| Leave behind | What to do |
|--------------|------------|
| Module globals, singletons, caches | A fresh object per test, or reset the global in teardown. |
| Open windows, widgets, timers, threads | Close and delete widgets in teardown. Stop timers and threads there too. |
| `os.environ`, `PATH` | Change them with `monkeypatch` so the next test sees the original. |
| Files | Write under `tmp_path`. |
| Database rows | Insert under a unique key this test owns, and delete that key in teardown. The test still passes when the table starts empty. |
| Mocks and patches | Undo them before the test returns. |
| Current directory | `monkeypatch.chdir(...)`. |
| Wall clock, network | Pass time in as an argument. Mark `network` or `smoke` when a test really must use the clock, the network, or a local service. |

### GUI / RPA windows

Top-level test windows open maximized, on one screen: the primary screen, or the screen named by `TEST_SCREEN`. A test that needs an exact size opts out with `@pytest.mark.windowed`. The suite passes headless (`QT_QPA_PLATFORM=offscreen`; on Linux with no display the fixture selects offscreen for that test and restores it). Close and delete widgets in teardown. Maintained copy: [tests/conftest.py](../tests/conftest.py). Qt is imported only when a binding is installed; the unit tier stays green without PySide or PyQt.

### Running

Use the project's own interpreter (its virtualenv, or the env that launches the app). The four-tier chain is [Run order (fail-fast)](#run-order-fail-fast). The agent runs that chain on the human's machine, reads the saved file, and reports the result ([Saved test output (agent runs it)](#saved-test-output-agent-runs-it)). The human does the in-app checks. Name which open PR merges first, and end with every open PR and what it is waiting on ([§ PR flow](#pr-flow)).

One tier, when that is all this run needs:

```bash
.venv/bin/python -m pytest tests/unit -q
```

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit -q
```

### Saved test output (agent runs it)

The agent runs the suite on the human's machine and reads the saved file. `logs/` is gitignored.

| File | Role |
|------|------|
| `logs\last_test_run.txt` | Latest run. Overwritten each time. |
| `logs\test_run_YYYYMMDD_HHMM_<tag>.txt` | Dated copy of that same run. |

`<tag>` comes from the current branch, in this order: `main` when the branch is `main`; otherwise `PR<n>` when `git config branch.<name>.pr-number` is set (`<n>` is that value); otherwise the branch name, with `\` and `/` replaced by `-`.

Delete only `test_run_*.txt` files older than 2 days. Leave `logs\last_test_run.txt` and anything else under `logs/`.

Hash `.env` before the run and again after it. The last line of the saved file is `ENV UNCHANGED` when the hashes match, and `ENV CHANGED - tell the agent` when they do not (or when the file appears or disappears). No `.env` file hashes as `none` on both sides, which is unchanged.

From the repo root (PowerShell):

```powershell
$stamp = Get-Date -Format 'yyyyMMdd_HHmm'
$branch = git rev-parse --abbrev-ref HEAD
$n = git config --get "branch.$branch.pr-number"
$tag = if ($branch -eq 'main') { 'main' } elseif ($n) { "PR$n" } else { $branch -replace '[\\/]', '-' }
New-Item -ItemType Directory -Force logs | Out-Null
$before = if (Test-Path .env) { (Get-FileHash .env).Hash } else { 'none' }
.\.venv\Scripts\python.exe scripts\run_tiers.py tests/unit tests/smoke tests/integration tests/regression 2>&1 | Tee-Object logs\last_test_run.txt
$after = if (Test-Path .env) { (Get-FileHash .env).Hash } else { 'none' }
$envLine = if ($before -eq $after) { 'ENV UNCHANGED' } else { 'ENV CHANGED - tell the agent' }
$envLine | Tee-Object logs\last_test_run.txt -Append
Copy-Item logs\last_test_run.txt "logs\test_run_${stamp}_$tag.txt"
Get-ChildItem logs\test_run_*.txt | Where-Object LastWriteTime -lt (Get-Date).AddDays(-2) | Remove-Item
```

**Report.** First line is **FAIL** or pass. Then the pass and fail counts for each tier, and which tier stopped the run. Then the `.env` line. Then each failed test by file and name. The human only does the in-app checks.

### Comments

Every fixture and helper documents each input (argument, fixture parameter, environment variable it reads) in its docstring.

### Capture on adoption (smoke tier)

Generate one capture script. One command runs it. Raw output stays in a gitignored folder. Capture shows the app booted and reached its important places, so it sits on **smoke** (the early warning). Integration is the happy path through the whole app.

| App | Script | Output |
|-----|--------|--------|
| GUI | Bind [scripts/capture_changelog_tabs.py](../scripts/capture_changelog_tabs.py) | PNG of the main window and tabs, headless where possible |
| Console, TUI, or other character UI | [scripts/capture_console_text.py](../scripts/capture_console_text.py) | Text files of the screens or commands |

`CAPTURE_OUTPUT_DIR` and `CAPTURE_TEXT_DIR` override the defaults (`data/Graphics/Screenshots/`, `data/ConsoleCaptures/`).

Change_Log thumbs are the curated slice of a GUI capture. [scripts/promote_changelog_shot.py](../scripts/promote_changelog_shot.py) turns one PNG into `docs/changelog_shots/` and prints the **Shot:** line ([§ Screenshots](#screenshots-each-push-that-paints-a-view)). The capture script does not commit those PNGs. Console captures have no thumbnail step.

**We do not push broken code (Allen lock 2026-10-16).** A pytest **FAIL** this session ran is a stop. **Fix it this session**, or **stop and discuss with the human** so it can be fixed. Do **not** `git push`, open a “ready” PR, or merge until that case is green **or the human in chat says push anyway**. `SHORTFALL:`, “unrelated,” “the other tier passed,” and “historical flake” are **not** waivers.

**Pre-existing fail.** If you can **prove** the same case was already red on `main` before this session started, that is not this session’s regression. Same turn: **identify who caused it** (commit, author, session) and **get them to fix it**, **or this session takes ownership and fixes it**. Parking it as SHORTFALL-only is not allowed. Unproven → treat it as ours: fix or discuss with the human. Do not push.

| Must | Must not |
|------|----------|
| Lead with **FAIL** if any pytest case failed | “All passed” / “suite green” while fails remain |
| **Fix it or discuss with the human.** No push / no squash-merge while a required-suite case (or any case this session ran) is still red. Proven pre-existing: name the owner this turn; they fix it or this session owns the fix | Disclose FAIL then land; wrap it as `SHORTFALL`; leave a pre-existing red parked |

### CI / pytest unfold (dormant until a threshold)

**Default is dormant.** A new app gets `tests/{unit,smoke,integration,regression}/` and runs those tiers in that order, stopping on the first failing tier. Day one is still `python -m pytest tests/unit -q`. It does **not** get GitHub Actions, `pytest-testmon`, or a canary harness on day one. Do not copy Stock_Data’s `src/testing/` or `.github/workflows/` until the human says yes.

**Threshold — unfold is due when any one is true**

| Signal | Why it is enough |
|--------|------------------|
| **≥ 25** collected unit tests (not kit stubs) | “Run everything” starts to hide failures |
| A `scripts/testing/` suite runner exists | Tiers are already a product |
| The human asks for CI / GitHub Actions | They named the need |

**Then one purple pick** (Recommended first, **Decide later** on the same card). Do **not** unfold silently. Do **not** re-ask every session — write the answer in ToDo.

| Pick | Agent does |
|------|------------|
| **Unfold Stock_Data-style pytest (Recommended)** | Canaries are a sniff list inside the unit tier (canaries first within unit), then smoke, integration, regression. Local `--impacted` via **pytest-testmon**. The workflow runs that same order, **no** `--impacted` on CI (clean runner has no testmon map). Gitignore `.testmondata`. OOP `TestLane` list, not a tier-string switch. Reference: Stock_Data `src/testing/` + `scripts/testing/run_smoke_suite.py` + `.github/workflows/unit-tests.yml`. |
| **Stay dormant** | Keep pytest local only. Record the skip in ToDo. |
| **Decide later** | Same as Stay dormant until they pick again. |

**Unfold shape (when they choose Recommended)**

1. `tests/{unit,smoke,integration,regression}/` — cases stay `test_*` functions unless the app already uses classes. Run in that order. Stop on the first failing tier.
2. `canaries.json` — a short sniff list (typical moles) that runs **first inside the unit tier**, before the rest of unit.
3. Suite script under `scripts/testing/` with `--tier` and optional `--impacted`.
4. `pytest-testmon` in requirements; `.testmondata` gitignored; `--impacted` is **local only**.
5. `.github/workflows/` job: `windows-latest` (or the app’s OS), pip + `requirements.txt` (not a private conda env). Order: canaries, then the rest of unit, then smoke, integration, regression. No `--impacted`.

Until that pick, agents: no workflow YAML, no testmon dependency, no canary package.

### Cyclomatic complexity (new / changed code)

When a slice of application code is done, score **touched functions** (McCabe). Stock_Data: `python scripts/score_cc.py <files>` (same visitor as the Tech Debt tab).

| | Gate |
|--|------|
| **Target** | CC **≤ 10** |
| **Too high** | CC **> 15** — split or a named leave-whole note |

Uncle Bob (Matt Pocock 2026-08-19) ran a **Complexity Score** (complexity × coverage) first on agent output — human **< 4**, agents **6–8**. A Tech Debt / hotspot table (CC × churn) is the cousin you can ship before coverage is in the loop. Do not invent a second formula.

## Executable production

When the app is packaged as an executable (or any other release build), an app expected to run for days or weeks needs a **long-run leak check** before that build ships. A short session will not show the leak.

1. **Code review** for common leak sources:
   - UI objects created per refresh and never freed
   - Timers and signal connections remade each cycle
   - Caches or lists that grow without pruning
   - Re-reading a growing file instead of tailing from an offset
   - DB, HTTP, socket, or child-process handles not closed
   - Day-rollover state not released
   - Unrotated logs
2. **Accelerated soak.** A regression test that runs under `running_under_tests()`, skips real waits, and drives thousands of refresh cycles and many simulated day rollovers in seconds. It fails if memory (`tracemalloc`, or object counts) keeps climbing instead of leveling off.
3. **Hourly RSS.** The running app logs its memory use (RSS) at DEBUG about once an hour, so a real multi-day run can confirm growth flattened.

## Migrations / schema (if DB included)

- Versioned SQL or migration tool of choice.
- Document apply order in a short runbook.
- Backup before destructive migrations.
- **SQL text lives in files** (Coding_Standards § SQL lives in files): queries and DDL are `.sql` (or migration files), not string literals in app code. App code loads and runs that text.
- Same change series: delta/migration + embedded/schema SQL the app applies + docs (Schema / runbook) when the live schema moves.

## Parallel sessions (mandatory)

Requires Grok Build 1.0.42 or newer.
1.0.5 reclaims idle checkouts under `~/.grok/worktrees` when safe and never deletes the last copy.
1.0.19 adds `--worktree` to headless `grok -p`.
1.0.42 adds `grok worktree create` (managed worktree, no session).
A Grok worktree is a detached checkout at the base commit. It does not create a branch. Ending a session does not remove it. Land with ordinary git. Remove with `grok worktree rm` or `grok worktree gc --max-age 7d`.

Git workflow detail: read [`.grok/skills/git-workflow-and-versioning/SKILL.md`](../.grok/skills/git-workflow-and-versioning/SKILL.md).
Second-writer worktree rules and branch-delete rules in this file override that skill.
Skill owns commit shape, message style, and PR detail. This file owns when a worktree exists and that the branch dies with the merge.

**Lock:** two chats in one folder share one checkout. A Grok worktree is a **detached** checkout at the base commit. It is not `git worktree add -b wip/<topic>`. Never edit the primary checkout while another Grok session is editing.

### Start

- **One writer, short task:** stay in the primary checkout. No worktree. No branch until the diff is worth keeping.
- **Second writer, or a task long enough that another writer may start:** Grok managed worktree, detached, off current `main`.
  - **CLI:** `grok -w --ref main`
  - **No session yet:** `grok worktree create`
  - **VS Code:** purple pick, **recommended only in this case**. Label it as a detached Grok worktree. Do not use `git worktree add -b wip/<topic>`.
- **Subagents that edit files:** `isolation: worktree`. Read-only children need no worktree.
- If this session is **already** in its worktree and the first message is a continuation → stay. No pick.
- Stage **only** this session’s files. Never `git add -A`.

**VS Code Grok Build** — purple multi-pick **only** when a second writer (or a long task) needs a worktree. Recommended first, marked **`(Recommended)`**:

| Human picks | Agent does |
|-------------|------------|
| **Detached Grok worktree (Recommended)** | Use a Grok managed worktree off current `main` (`grok -w --ref main` / `grok worktree create`). Tell them the folder path. **Do not** run `git worktree add -b wip/<topic>`. **Do not keep editing the primary tree.** |
| **Stay in this tree** | Stay only for one writer, short task, in the primary checkout, with no other Grok session editing. If this is the primary tree and another Grok session is editing → **stop**. Do not `checkout -b` here to “make room.” |
| **Other** | Name they typed: same create path as Detached Grok worktree. |

### During

- Do not leave uncommitted changes that another session could see in a shared checkout.
- Never assume shared state, open files, or previous multi-select answers from another session.

### Database (single-threaded)

Worktrees copy `.env`, so they all talk to the **same** database. Schema, migrations, and store DDL are **not** isolated.

Before any database change (migrations, schema SQL, destructive store work):

1. Run `git worktree list`.
2. This session must be the **only topic worktree**. The primary checkout on `main` may remain. A second topic worktree means **stop**.
3. Tell the human. Do not migrate while another session can run the app or apply its own DDL against that database.

Idle leftover folders still count until they are removed. Isolating databases per worktree is later work; until then this gate is the fence.

### Purple multi-picks (do not time out)

The human answers purple cards when ready. They **must not** expire.

| Layer | Lock |
|-------|------|
| Grok CLI / TUI | `~/.grok/config.toml` **and** `~/.grok/requirements.toml`: `[toolset.ask_user_question] timeout_enabled = false`. Do not turn **Ask-Question timeout** on in `/settings`. |
| VS Code Grok Build | `grok.acp.promptIdleTimeoutMs = 0` (User settings **and** the workspace). `0` disables the 30-minute idle cap. Applies to **new** sessions. |

### Abort

If a permission / multi-select **still times out** (old session started before the lock, or a host bug): treat the session as aborted. Do not continue in the same tree.

### Wrap-up

When finished:

1. `git switch main && git pull --ff-only`.
2. If [§ PR flow](#pr-flow) is at `hold: 3 open`, say that and do not open another PR. Otherwise, if the diff is worth keeping **and required tests are green** ([§ Tests](#tests)): branch off that `main`, commit (stage only this session’s files), squash-merge, delete the local branch and the remote branch. A detached worktree that dies is a folder, not a branch. A known pytest FAIL → fix it or discuss with the human; `Done` (hold) until then, not `Push Complete`.
3. After merge: `grok worktree rm <id>` if this session used a managed worktree. Do not delete the primary checkout.
4. Finish pass: `grok worktree list`, `git worktree list`, `git branch -vv`. A branch with no worktree and no open PR is trash. Idle worktrees count until removed.
5. Last line: `Push Complete` when the PR is open or landed. Use `Done` only when work is finished locally and **not** pushed (abort / hold).

### Wrong base (no unique commits)

```text
git stash push -u -m "wip notes"
git reset --hard main
git stash pop
```

If the checkout has unique commits to keep: `git rebase main` in that folder (not reset). A detached worktree that dies is a folder, not a branch.

Agent checklist: root [AGENTS.md](../AGENTS.md) § Parallel Session Rules.

## PR flow

Allen lock **2026-10-27**. For the assistant that opens and lands pull requests. PRs left open while newer merges land go stale and conflict.

1. **WIP limit of 3.** Count open PRs that are not yet tested and merged. At 3, say `hold: 3 open` and start no new PR until one merges.
2. **During a hold,** the user's new ideas go into [ToDo.md](ToDo.md) and ride along in the next PR. Do not start that work. Only a real bug found in a PR under test is added to that PR.
3. **Every test command names which PR merges first,** so nothing builds on an unmerged PR.
4. **24 hours untested.** Flag a PR that has sat untested for 24 hours (a nightly check is enough) so it gets tested, merged, or closed. Do not add GitHub Actions for this. CI stays dormant until [§ CI / pytest unfold](#ci--pytest-unfold-dormant-until-a-threshold).
5. **Every test command ends with the open list:** one short plain-words line per open PR and what it is waiting on. Example: `#250 is waiting on your test. #236 is ready for you to say merge.` The human sees how many are open without asking.

## Handoff to human

Short: what changed · files · how to verify · docs · branch landed and deleted · worktree removed if any. A test command follows [§ PR flow](#pr-flow).

## Solo / small team (keep light)

See [Project.md](../Project.md) § Lightweight practices. In short: shippable main, read your own diff, lock dependencies, update ToDo/Change_Log with the code.
