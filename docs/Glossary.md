# Glossary (portable starter)

Shared vocabulary for humans and agents. **Add product terms here** as the app grows.

| Term | Meaning |
|------|---------|
| **Staff kit** | Portable process pack: AGENTS, PROCESS, Coding_Standards, Change_Log/ToDo/Lessons norms, test layout — first-class in git, updated with code. |
| **cache_key** | Structured identity for a data slice (e.g. tuple of entity / range / version). Not a UI page string. |
| **page_key** | Path-safe string identity for a UI page/document/slot (if the app has one). Prefer over vague “slug” for view caches. |
| **Mixin** | Small class that contributes one behavior slice via composition/inheritance — not a god window. |
| **Unit test** | Supply inputs to a function and verify the outputs still match. No database, no network, no real window. |
| **Smoke test** | Key components work. The app boots and reaches the important places: external services (for example brokers or APIs), the database, and each core feature doing its core thing (for example charts, history, positions). If it fails, call the engineers before production users hit it. A real local service belongs here (this used to be called integration). The adoption capture sits on this tier. |
| **Integration test** | Run the whole thing from the start through key parts. Generally the happy path. |
| **Regression test** | The edge cases. Tiers run unit, then smoke, then integration, then regression. Pytest exit 5 (no tests collected) counts as pass. Any other failure stops the chain. |
| **Characterization test** | A test that records what the code does today, added before changing untested code. |
| **State leak** (leaked state) | Anything one test leaves behind that changes another test's result: module globals and singletons, caches, open windows or widgets, running timers or threads, environment variables and `PATH`, files, database rows, mocked or patched functions that were not undone, or the current working directory. Symptom: a test passes alone and fails in the full suite, or the other way around. |
| **windowed** | Pytest marker (`@pytest.mark.windowed`). The test needs an exact window size, so the default maximize-on-one-screen behavior stays off. |
| **Canary** | A tiny sniff-test that runs **first inside the unit tier**, before the rest of unit (typical moles). Stock_Data: `src/testing/canaries.json`. |
| **pytest-testmon** | Pytest plugin that re-runs tests whose code changed (`--impacted`). **Local only** — CI has no map. |
| **CI unfold** | Kit default: no GitHub Actions. When tests cross the PROCESS threshold, one purple pick. Canaries run first inside unit, then smoke, integration, regression. Testmon stays local. |
| **Change_Log** | User-visible history (Why / What / Benefit). |
| **ToDo** | Backlog; finished work leaves open columns. |
| **Worktree** | A Grok **managed** checkout (Grok Build **1.0.42 or newer**): detached at the base commit, **no branch**. One writer, short task: stay in the primary checkout. Second writer / long task: `grok -w --ref main` or `grok worktree create`. **VS Code:** purple pick recommended **only** in that second-writer case (label: detached Grok worktree). Do not `git worktree add -b wip/<topic>`. Ending a session does not remove it. `grok worktree rm` / `grok worktree gc --max-age 7d`. |
| **Done** | Last line of a finished Grok session that was **not** pushed (abort / hold). |
| **Push Complete** | Last line of a finished Grok session after the short-lived branch was pushed or squash-merged, local and remote branches deleted, and any managed worktree removed. |

## Libraries (common Python)

| Library | Role |
|---------|------|
| **pytest** | Test runner |
| **python-dotenv** | Load `.env` into process env |
| **psycopg** | PostgreSQL driver (v3) |
| **pandas** | DataFrames / tabular analysis |
| **numpy** | Arrays / numeric core under pandas |
| **PyQt6** | Desktop UI (if desktop app) |
| **requests** / **httpx** | HTTP clients |
| **pydantic** | Validated models / settings |

See [Libraries.md](Libraries.md) for a fuller menu and [Database.md](Database.md) for Postgres vs SQLite vs Timescale.

Delete unused rows; never leave secrets or personal data here.
