# Agent instructions — project template (staff kit)

Portable entry point. **Copy into each app** and replace the architecture paragraph.

## Architecture (one paragraph)

**YOUR_APP** is a … (fill: stack, data stores, UI shell). Prefer **named domain/session objects** over parallel `dict` caches for live state. Persistence is … (DB-first / files). Local runtime only: … (gitignore list).

## Context loading (mandatory)

**Never load the entire documentation set.** Open only:

1. Files listed in the **active** nested `AGENTS.md` for the directory you are editing.
2. Docs the task names.

## Start here (on demand)

| When | Open |
|------|------|
| Process / commits / PRs | [docs/PROCESS.md](docs/PROCESS.md) |
| Judgment / leave it better | [docs/Taste.md](docs/Taste.md) |
| Style / errors / size | [docs/Coding_Standards.md](docs/Coding_Standards.md) |
| Backlog | [docs/ToDo.md](docs/ToDo.md) |
| Surprises | [docs/Lessons_Learned.md](docs/Lessons_Learned.md) |
| Vocabulary | [docs/Glossary.md](docs/Glossary.md) |
| Kit spine | [Project.md](Project.md) |
| Setup / install | [README.md](README.md) (Environment setup) |

Run `git status` and `git worktree list` before editing. Stage **only** this session’s files. Never `git add -A`.

## Parallel Session Rules (mandatory)

Requires Grok Build 1.0.42 or newer.
1.0.5 reclaims idle checkouts under `~/.grok/worktrees` when safe and never deletes the last copy.
1.0.19 adds `--worktree` to headless `grok -p`.
1.0.42 adds `grok worktree create` (managed worktree, no session).
A Grok worktree is a detached checkout at the base commit. It does not create a branch. Ending a session does not remove it. Land with ordinary git. Remove with `grok worktree rm` or `grok worktree gc --max-age 7d`.

Git workflow detail: read `.grok/skills/git-workflow-and-versioning/SKILL.md`.
Second-writer worktree rules and branch-delete rules in this file override that skill.
Skill owns commit shape, message style, and PR detail. This file owns when a worktree exists and that the branch dies with the merge.

- **One writer, short task:** stay in the primary checkout. No worktree. No branch until the diff is worth keeping.
- **Second writer, or a task long enough that another writer may start:** Grok managed worktree, detached, off current `main`.
  - **CLI:** `grok -w --ref main`
  - **No session yet:** `grok worktree create`
  - **VS Code:** purple pick, **recommended only in this case**. Label it as a detached Grok worktree. Do not use `git worktree add -b wip/<topic>`.
- **Subagents that edit files:** `isolation: worktree`. Read-only children need no worktree.
- **Never** edit the primary checkout while another Grok session is editing.
- Stage **only** this session’s files. Never `git add -A`.
- Do not leave uncommitted changes that another session could see in a shared checkout.
- Never assume shared state, open files, or previous multi-select answers from another session.
- **Database changes are single-threaded.** Worktrees share one database when they copy the same `.env`. Before DDL, migrations, or store schema work: `git worktree list`. This session must be the **only topic worktree** (primary checkout on `main` may remain). If another worktree is in play, **stop** and tell the human. Do not migrate while another session can use the database.
- Secrets: never commit `.env`, tokens, dumps, or local override configs.

**Land (both cases):** `git switch main && git pull --ff-only`. If the diff is worth keeping **and required tests are green**: branch off that `main`, commit, squash-merge, delete the local branch and the remote branch. A known pytest FAIL does not land — fix it this session or discuss with the human. At three open PRs not yet tested and merged, say `hold: 3 open` and do not open another ([docs/PROCESS.md](docs/PROCESS.md) § PR flow). A detached worktree that dies is a folder, not a branch.

**After merge:** `grok worktree rm <id>`. Do not delete the primary checkout.

**Finish pass:** `grok worktree list`, `git worktree list`, `git branch -vv`. A branch with no worktree and no open PR is trash. Idle worktrees count until removed.

**Resume:** already in this session’s worktree and the first message is a continuation → stay (no pick).

Purple multi-picks **must not time out**: CLI `[toolset.ask_user_question] timeout_enabled = false`; VS Code `grok.acp.promptIdleTimeoutMs = 0`. If a pick **still** times out (old session / host bug): abort; do not continue in the same tree.

Full write-up: [docs/PROCESS.md](docs/PROCESS.md) § Parallel sessions.

## Global coding standards (short)

- **Leave the code better than you found it** (Scout outdoor code). Slice is as good or better (bugs, speed, clutter, reliability). [Taste.md](docs/Taste.md).
- Type hints on public functions; explicit imports.
- Centralize errors; redact secrets in logs.
- Rule of Three before extracting shared helpers.
- **Do not hardcode** paths, URLs, runtime file names, hosts, or ports (Allen lock — no exception grant). `.env` / config / derive. [Coding_Standards.md](docs/Coding_Standards.md).
- Prefer domain/session objects over new parallel maps.
- **SQL lives in `.sql` files**; app code loads and runs it — see Coding_Standards.
- Tests under `tests/{unit,smoke,integration,regression}/`, run in that order, stop on first failing tier. Pytest exit 5 (no tests collected) counts as pass. Every feature or fix ships with a test ([tests/README.md](tests/README.md)). **CI/CD stays dormant** until PROCESS § CI / pytest unfold (then one purple pick — do not scaffold GitHub Actions or pytest-testmon on day one).
- Docs hygiene with the code: Change_Log / ToDo / Lessons when PROCESS requires it.
- Commits: clear subject; optional trailers `Assisted-by: Grok Build`.

| Tier | Meaning |
|------|---------|
| **unit** | Supply inputs to a function and verify the outputs still match. No database, no network, no real window. |
| **smoke** | Key components work. The app boots and reaches the important places: external services (for example brokers or APIs), the database, and each core feature doing its core thing (for example charts, history, positions). If it fails, call the engineers before production users hit it. A real local service belongs here (this used to be called integration). |
| **integration** | The whole thing from the start through key parts. Generally the happy path. |
| **regression** | The edge cases. |

## How this session works

This session does the work. Nested `AGENTS.md` files are extra reading lists for that folder. Replies start with the answer. No role label on the first line (`main:`, `dba:`, `ui:`, or any other).

## Always-on checklist

| Question | Action |
|----------|--------|
| **New / concurrent / long-running session?** | One writer, short task: primary checkout, no worktree, no branch until the diff is worth keeping. Second writer or a long task: Grok managed worktree (`grok -w --ref main` / `grok worktree create`). **VS Code:** purple pick **recommended only** for that second-writer case (detached Grok worktree). **Never** edit the primary checkout while another Grok session is editing. Requires Grok Build 1.0.42 or newer. |
| User-visible change? | Change_Log row (Why / What / Benefit) |
| User-visible **view paint**? | Run the app, screenshot each modified view, `python scripts/promote_changelog_shot.py`, add **Shot:** — PROCESS § Screenshots |
| Click-path tutorial (`docs/tutorial/`)? | Same series as UI or backend-that-affects-UI: update the matching tutorial page (PROCESS § Screenshots) |
| Backlog item? | Update ToDo |
| New API / persistence / UI flow? | Test under `tests/` |
| New feature, bug fix, or edit to untested code? | Ship a test with the change. Bug fix: a failing test first. Untested code you touch: a characterization test. Adopting an app: unit tests for the core logic, a smoke check that key components work, and a capture script (GUI PNG or console text). [tests/README.md](tests/README.md). |
| Testing past the kit stub? | If ≥25 unit tests, a suite runner, or the human asked for CI → **one** purple pick to unfold Stock_Data-style pytest (PROCESS § CI / pytest unfold). Do not unfold silently. |
| **Leave the code better?** | Slice is as good or better (bugs, speed, clutter, reliability). Knowingly worse does not ship. [Taste.md](docs/Taste.md). |
| **Known pytest FAIL?** | **Do not push. Do not merge.** Fix it this session, or stop and discuss with the human. Proven pre-existing: name who caused it this turn; they fix it or this session owns the fix. `SHORTFALL` / “unrelated” / “the other tier passed” are not waivers. [PROCESS.md](docs/PROCESS.md) § Tests. |
| **Running the suite?** | The agent runs it on the human's machine, saves `logs\last_test_run.txt` plus a dated copy, and reports pass/fail counts, the `.env` line, and failures by file. The human does the in-app checks. [PROCESS.md](docs/PROCESS.md#saved-test-output-agent-runs-it) § Saved test output. |
| **Three open PRs?** | Say `hold: 3 open` and start no new PR until one merges. New ideas go to `docs/ToDo.md`. Every test command names which PR merges first and ends with every open PR and what it waits on. [PROCESS.md](docs/PROCESS.md) § PR flow. |
| New / changed application code? | Cyclomatic complexity on touched functions — **CC ≤ 10** target, **CC > 15 too high** (PROCESS § Cyclomatic complexity) |
| **Executable for a days-or-weeks run?** | Long-run leak check before the build: leak review, accelerated soak under `running_under_tests()`, hourly DEBUG RSS. [PROCESS.md](docs/PROCESS.md) § Executable production. |
| Non-obvious fix? | Lessons_Learned |
| Database / schema change? | Single-threaded: `git worktree list` — this session must be the only topic worktree, then migrate. |
| **Hardcoded path, URL, file name, host, or port?** | **Stop.** Put it in `.env` / config or derive it. Allen does not authorize one-off literals. [Coding_Standards.md](docs/Coding_Standards.md) **Do not hardcode**. |
| Secrets? | Never commit |

## Do not commit

`.env`, tokens, dumps, local override configs, large binaries unless intentional.
