# Coding standards (portable kit — a priori)

Application-agnostic rules. Copy this file into each app. Product paint, broker quirks, and session graphs stay in that app’s **application-specific** standards.

Stock_Data splits: index `docs/Coding_Standards.md`, a priori `docs/coding_standards/a_priori.md` (keep those two in sync with this file).

---

## Highest priority — clarity and intent

Every reader should understand **why** code exists and **what** it does without spelunking.

### Leave the code better than you found it (Allen lock)

Scout outdoor code: leave the place better than you found it. The place is this codebase. A slice ships when the tree is **as good or better** than when the session started (bugs, speed, clutter, reliability). Knowingly worse does not land. Customer satisfaction is the scoreboard; we do not get to keep coding if the customer loses too much trust. Full text and Scout Law: [Taste.md](Taste.md).

### Who is the computer here? (Allen’s motto)

> **“Who is the computer here?”**  
> Don’t make the user do work the computer should have taken care of.  
> Let the user do what the user is good at.

| User is good at | Computer is good at |
|-----------------|---------------------|
| Naming things they care about (`IRA`, `Roth`) | Mapping nicknames to opaque broker IDs / last-4 |
| Choosing symbols and time ranges | Parsing configs, merging sources, re-painting labels |
| Judging whether a chart *looks right* | Dual fences, gates, retries, serialization |
| Writing one friendly `.env` line | JSON shape, schema, hash keys, re-sync |

**Design implications**

1. Prefer **human-editable** surfaces for human intent (e.g. `ACCOUNT_ALIASES=IRA 4797;Roth 5531` in `.env`) over hand-editing nested JSON unless the product already has a UI for that field.
2. When both exist, **merge with a clear override** (document which wins) — do not force the user to keep two files in sync by hand.
3. Never require the user to re-enter broker account hashes, paste opaque API types, or re-sync just to rename a label the app can re-apply on paint.
4. Automate repetition: re-apply aliases on every paint path; don’t make “edit JSON then full re-sync” a ritual.
5. Agents: if a task would push bookkeeping onto Allen, stop and implement the automation instead.


### Do not hardcode values that will change (Allen lock)

**Allen does not authorize hardcoded paths, URLs, file names, hostnames, ports, or other literals that are likely to change.** Do not ask for a one-off exception. Put the value where another machine can set it, or derive it.

A string that is wrong on a second PC, a second clone, or next year does not belong in Python (or SQL) as a literal — **even once**. Rule of Three “once is fine inline” does **not** apply here.

| Kind | Lives |
|------|--------|
| Machine paths, token files, interpreter, log files | `.env` / Settings (absolute after first resolve). `.env.example` documents the **key** and a relative placeholder — never `C:\Users\...` |
| Product catalogs | Tracked config JSON / Settings |
| Clone root, linked worktree | Derive (`Path(__file__)`, `git rev-parse`) |
| Vendor API / OAuth / portal URLs, host, port | `.env` key; default placeholder only in `.env.example` |

| Do | Don’t |
|----|--------|
| Absolute file path in `.env` (`TOKEN_PATH=…`) | `Projects/YourApp` or `C:\Users\Allen\...` in `src/` |
| Read callback / API base URL from `.env` | Paste a vendor `https://…` into a helper as the only source |
| Name this repo’s own modules and shipped `sql/*.sql` files | Invent a second runtime filename in code (token path, log path, Desktop dump folder) |

**Not this rule:** Python package names in this repo, test `tmp_path` fixtures, and protocol tokens required to *validate* a value the user already set (`https` as a scheme check). Those are this codebase, not this computer.

If a new runtime location appears: add the `.env` / config key, persist it, document the key in `.env.example`. Do not bake one person’s folder layout into the program.


### Tradition vs dead peer pressure

**Continuity has value.** Momentum, shared habits, and “we already know this path” help teams ship. Some people (structure/process-first temperaments) need that ballast. Respect it: do not thrash names or fences for sport.

**Tradition alone is not a design reason.**  
> “Tradition is peer pressure from dead people.”

**Cardinal sin:** defending a name, API, env var, path, or process **only** because it is familiar or already shipped — with no invariant, no caller load, no safety argument.


### Close enough is not close enough (Allen lock)

This is **stock trading software** that can sit in front of **hundreds of thousands of dollars**. **Exact** is the only acceptable default. “Close enough,” “good enough,” “substantially spans,” a 5-calendar-day slack, or skipping a user **Refresh** because the cache said current — those are **cardinal sins** unless Allen **explicitly** permits that shortcut for that case.

| Sin | Correct response |
|-----|------------------|
| “Coverage is within 5 days of Range start.” | Count the **exact** sessions he asked for (Trading Days = NYSE sessions, not weekends/holidays). |
| “Last bar is recent; skip Schwab.” | If the last painted session is before the lookback end, **fetch the missing sessions**. |
| “User hit Refresh but fetch_needed=0.” | **Refresh always asks the broker.** Cache-current is not permission to no-op. |
| “Leave a gap; expand later.” | Do not ship a graph that is short of the stated Range. |

If you choose a shortcut for speed, **name it as a SHORTFALL in that turn** and **ask** — do not bury it.

| Sin | Correct response |
|-----|------------------|
| “Keep `HOP_*` env aliases — we always had them.” | Rename to the right words; update the few callers; delete the old names in the **same** change series. |
| “Replace-all would be noisy.” | Noisy once beats permanent dual vocabulary and agent confusion. |
| “Leave a legacy fallback for a year.” | Fallback is a **dated** migration aid (days/weeks, named owner, tracked ToDo) — not an eternal second name. |
| “Chesterton’s fence says never rename.” | Fence protects **invariants** (why the guard exists), not **branding** or obsolete jargon. |

When vocabulary is wrong (generic, actor-free, or lying): **change it**. Do not hold the codebase hostage to the past with infinite `legacy_*` aliases. Document the rename in Change_Log; greppable old tokens should be **gone**, not “still accepted.”

### Chesterton’s fence — Indiana Jones the idol

> **“Never take down a fence until you understand why it was put there in the first place.”**  
> — G. K. Chesterton (paraphrased)

Prove the old system is obsolete **and** that you can replace what it protected before you yank it. Swap the idol for a bag of sand that still holds the weight — then leave.

**Caveat (the temple still collapses sometimes):** even a careful swap can miss a hidden tripwire. That is why dual fences, smokes, and Lessons exist — not why we freeze bad names forever.

Before removing, short-circuiting, or “simplifying” a guard, gate, timer, or dual path:

1. **Find the fence.** Name the failure mode it was built for (comment, Lessons_Learned, Change_Log, smoke contract, or git blame).
2. **State both sides.** What breaks if it stays? What breaks if it goes?
3. **Keep both constraints** when they are independent — do not trade A for B by deleting A’s fence.
4. **If you must change it**, replace with a design that still enforces the original invariant (comment the lesson; extend smoke). Do not leave “cancel only” after a path that used to “cancel + re-arm.”
5. **Watch for hidden gotchas** after the swap (paint + prefetch, load time + beauty). One green unit test is not the whole temple.


### Warnings are almost always a deeper problem

**Do not ignore, hide, or “squelch” warnings.** A warning is nearly always a signal that the design, process, or environment is wrong — not a cosmetic log line.

| Do | Don't |
|----|--------|
| Read the full warning; understand **why** it fires | Filter stderr, demote severity, or collapse messages so the console “looks clean” |
| Fix root cause or **re-engineer the process** so the warning does not appear | `# noqa` / `except Exception: pass` / log-and-continue without a dated plan |
| Document *expected vendor noise* only when proven harmless **and** still surface it (full text in logs, no drop of other lines) | Assume “exit code 0 ⇒ ignore stderr” |
| Gather evidence (especially **log hit %**) and **email the vendor** with user-base impact (time and/or dollars when you can) | File “it’s noise” locally and never tell the vendor |
| Treat repeated production warnings as **P1 design debt** | Ship “we’ll watch it” without a ToDo owner and exit criteria |
| A local pytest **FAIL**: **do not push / do not merge**. Fix it this session or discuss with the human. Proven pre-existing: name who caused it this turn; they-fix or we-own-and-fix | Disclose FAIL then land; wrap it as `SHORTFALL`; leave a pre-existing red parked |

**Rule of thumb:** squelching or ignoring warnings will **~99% of the time** become a production-down issue later. Prefer changing the architecture (e.g. dump format, API flow, schema ownership) so the tool has nothing left to warn about — not teaching the operator to look away.

**Chesterton’s fence still applies:** if a warning is truly vendor-catalog noise (example: Timescale `continuous_agg` circular FKs on a full `pg_dump`):

1. **Prove** it is catalog noise, not our bug.
2. **Keep** a full log line; never drop sibling warnings; document restore implications.
3. **Gather evidence**, especially **log hit percentages** (share of lines, how often operators see it, over what window).
4. **Generate an email to the vendor** that shows the impact of their design deficit on the user base. Translate those numbers into **time and/or dollar impact** whenever you can (operator hours, delayed restores, missed alerts).

That is **not** a license to silence the next unfamiliar warning.

### ADR references in code

Accepted decisions live under [docs/adr/](../adr/). **Implementation sites must be discoverable from code:**

| Rule | Detail |
|------|--------|
| **Module or package that owns the decision** | Module docstring (or top-of-file comment) names the ADR, e.g. `See docs/adr/0002-event-type-is-posture.md`. |
| **Non-obvious fence or branch** | One-line comment at the guard: which ADR or Lessons entry it protects. |
| **New ADR accepted this session** | Same commit series: code comment or docstring link, not docs-only. |

Do not paste the whole ADR into source. A path plus a short phrase is enough. Agents: if you implement an ADR and leave zero code pointers, that is incomplete hygiene.

**ADR vs Lessons_Learned:** ADR = lasting **choice**. Lessons = short **discovery** after a surprise. Same topic can have both (lesson first, ADR when the rule hardens).

### Prefer positive names and positive prose

**Variables and flags:** name the present, successful, or allowed state — then invert in code if needed.

| Prefer | Avoid |
|--------|--------|
| `has_bars`, `is_ready`, `paint_ready` | `no_bars`, `not_empty`, `missing_data` as primary names |
| `allow_prefetch`, `bars_present` | `disable_prefetch_unless…` without a positive twin |
| `errors_remaining == 0` after counting successes | chains of `not fewer`, `not missing`, `if not empty` |

**Prose (agents and docs):** Prefer **do-form** sentences. When you start with “Not …”, continue with what *is* true or what *to do*, using positive terms (complete, present, larger, keep). Avoid stacking “not fewer / not empty / never without” in one clause — rewrite as “keep at least N” / “require a complete set” / “always pair with X”.

**Active voice (agents and ADRs especially):** Prefer **subject–verb–object** with a clear actor. Passive constructions hide who acts and invite cryptic shorthand.

| Prefer (active) | Avoid (passive / actor-less) |
|-----------------|------------------------------|
| `ensure_events_for_chart` runs policies and writes missing event rows when OHLCV bars exist. | Chart ensure path can fill missing TFs from policies when bars exist. |
| We store posture in `events.event_type`. | Posture is stored in `events.event_type`. |
| Agents must propose session fields. | Session fields should be proposed. |

Allen’s note: double-negative framing and passive jargon force extra mental decoding; positive active form keeps staff and agents aligned.

### Classes and major functions

- **Every class** needs at least a **one-line docstring or comment** in plain English: why it exists and what responsibility it owns.
- **Every major function** (public methods, module entry points, non-trivial helpers) needs the same — one clear line minimum.
- Comments explain **intent and trade-offs**, not a line-by-line restatement of the code.

### Type means a shared interface (Jim Wilson)

> Whenever you find a “Type” of something, that usually means it needs to be multiple inheritance with a common interface to implement.
> — Jim Wilson, Aion Expert

A `kind` / `type` string plus `if kind == "trade"` / `"event"` / `"bar"` is a missed interface. Those objects are the same *kind of participant* (something under the pointer, something that paints, something that takes a click). Give them **one interface** (Python: ABC or Protocol mixins) and **one object that implements several** (paint + hit-test + hover). Dispatch by calling the interface across a **list of instances**, not by switching on a string.

A switch is acceptable only for a closed pair that will not grow (true vs false). The moment there is a third “type of X”, it is a list of interface implementers.

The other extract: the **same bundle of facts** threaded through many functions (see Rule of Three — named instance).

**Do not add a second identifier.** A `kind="psar"` string beside `isinstance(item, PsarOverlay)` is the kind switch in disguise. The **class is the identifier**. GUI toolkits already do this (`isinstance` / `qobject_cast`, Qt `QGraphicsItem.type()` with `UserType`). One object can inherit toolkit + domain interfaces. Two parallel IDs for the same object will drift.


### Functions

Quotes from Robert C. Martin, *Clean Code* (Prentice Hall, 2008), Chapter 3 — Functions:

> Functions should do one thing. They should do it well. They should do it only.

> The first rule of functions is that they should be small. The second rule of functions is that they should be smaller than that. […] Functions should not be 100 lines long. Functions should hardly ever be 20 lines long.

How you know it is doing more than one thing:

> Another way to know that a function is doing more than “one thing” is if you can extract another function from it with a name that is not merely a restatement of its implementation.

Command vs query (do not mix a mutation with a returned answer):

> Functions should either do something or answer something, but not both. Either your function should change the state of an object, or it should return some information about that object. Doing both often leads to confusion.

**House rules that follow from that**

- **One job per function.** If a block can be named as its own step (not a restatement of the next line), extract it.
- **Prefer a single return *value*.** Callers get one object (dataclass, named tuple, or a documented dict) — not several unrelated bare values. This is **not** Dijkstra’s single-exit (`return` only at the bottom). Early `return` / exceptions are fine; mixing “here is the answer” with “and I also mutated X” is not (command-query split above).
- **Keep functions short** — one job, typically far under a screen. The **~500-line** split signal is for **files** (below), not functions. A 500-line function that returns one object still failed “small” and usually failed “one thing,” unless every inner line is a field of that same object and an extract would only restate `row.qty = payload["quantity"]`.
- **Meaningful names** over abbreviations — `plan_minute_fetch_windows`, not `pmfw`.
- **Few arguments** — more than three or four parameters is a signal to introduce a small options object or dataclass.
- **Cyclomatic complexity (CC)** on new or changed functions: **target ≤ 10**, **too high > 15** (split or name a leave-whole exception). Same McCabe idea as a Tech Debt hotspot table. Uncle Bob **Complexity Score** (CC × coverage): human **< 4**, agents **6–8** — run that when coverage is in the loop; do not invent a second formula. See PROCESS § Cyclomatic complexity. CC does **not** catch a dense one-liner (a filtered comprehension is still CC 1). See **Dense one-liners** below — explain first; split only when a straightforward comment cannot name the line.

### Files

- If a **file** grows past **~500 lines**, look for a real seam and split (new module, class, or package). `stock_ui.py`, `window_layout.py`, and `src/ta_plot/backends/chart_surface.py` are known large files — split only with a named destination, not `foo_part2.py`.
- **Split order.** The original bytes must exist in a **second place** before you replace the first. Copy the class to the new file, or `git mv` the fat file then write a new door, or park via temp / `git show HEAD:path`. Do **not** overwrite the source path in the same turn as a read of that path — parallel tool calls on one file are a race.
- **Package vs property façade.** `foo.py` → `foo/` with named modules and `__init__.py` re-exports is boot-time import cost. Wrapping the old god object in `@property` aliases so callers keep `host._foo` is a SQL-style view on the **hot path** — each paint hop pays Python lookup. Split by moving classes; bind locals in loops; do not paper over the cut with properties.
- **No leftover-name aliases (Allen lock).** After you extract a collaborator, **retarget remaining call sites in the same series** and **delete** the old name. Do **not** add `@property` / getters so `host._old` still works. That is a time-saver, not a finished split. Exception **only** if the **app would otherwise fail to run**, plus a dated ToDo to delete the aliases. Git / project stats key **commits and files**, not private field names.
- **Why split at all:** so the **hot sections** (high complexity × high rework) become their own files, not to hit a line quota. File-level Tech Debt only names the warehouse. Rank functions/classes inside it before carving. See ToDo **Tech Debt: score sections inside large files**.
- Physical line count includes comments, data tables, and tests. Use it as a **review flag**, not an automatic extract.

**Leave the file whole when:**

1. **One job, one module** — the file *is* the seam (one TAP backend, one statement parser). A same-package `*_part2.py` that only this file imports is a fake split.
2. **Shared private state** — methods share one fat instance (plot items, ViewBox, overlays). Extracting them into new modules forces a parameter bag or circular imports. Mixins already hurt Chart presenter.
3. **Call-order / paint invariants** — reveal, prefetch, PyQtGraph paint: sequence *is* the bug. Scattering the path across files makes dual-fence regressions more likely.
4. **No second copy yet** — Rule of Three. Do not extract `window_layout.py` until there is a real destination package, not a speculative helper.
5. **Test catalogs** — long `test_*.py` files that are case tables, not a god class. Split when navigation hurts, not at 500 on principle.
6. **Replacement is scheduled** — do not slice a module you are about to delete (legacy Plotly HTML path, etc.).
7. **Hotspot in season** — a high Tech Debt score can mean “this is the live surface.” Splitting it *while* it is changing multiplies merge conflicts; wait for a seam after the burst.

### Imports

- **Each import line** (or tight group from the same package) carries an **inline end-of-line comment** stating why that dependency is needed in this file.
- Prefer standard library → third party → local `src` order; one blank line between groups.

Example:

```python
import json  # snapshot persistence for option delta history
from pathlib import Path  # repo-root resolution for data files

import pandas as pd  # flatten option chain maps into tabular rows

from src.schwab import SchwabClient  # authenticated option chain fetch
```

### Uncle Bob / Clean Code summary

| Principle | Rule of thumb |
|-----------|----------------|
| Single Responsibility | One reason to change per module/class/function. |
| Open/Closed | Extend behavior with new functions or small types, not copy-paste branches. |
| Readable flow | Read top-to-bottom like a narrative; extract nested blocks that obscure the story. |
| Error handling | One place formats errors; callers display or log, they do not re-word. |
| Duplication | See Rule of Three below. |
| Side effects | Make I/O and mutation obvious; pure logic separated where practical. |
| Tests / smoke | Behavior changes get a smoke script or test when feasible. |

### Applying these rules

- **All new code** follows this document on first commit.
- **Existing code** is updated incrementally when a file is already being changed for a feature or fix — do not boil the ocean in one PR.

### Block-level intent comments

Non-trivial blocks need a short comment stating **why** the block exists (optional one line on **what** it does). Apply at:

- Multi-step startup or reveal sequences (disk warmup, veil, prefetch deferral)
- Framework workarounds (Plotly relayout, WebEngine hidden paint, Qt thread boundaries)
- Guards and early returns whose reason is not obvious from names alone

One line above the block is enough. Do not narrate every assignment.

### Dense one-liners (explain first)

Powerful, meaningful, clean one-liners are welcome. McCabe CC will not flag them (a filtered comprehension is still **CC 1**).

**Priority:** put a **one-line English comment above** that states the outcome (and what a sentinel like `"?"` means). Split the line apart only when you cannot explain it in a straightforward way — the comment would have to walk through the syntax instead of naming the result.

Triggers that need that comment (or a split if the comment fails):

- Comprehension with an `if` filter
- Nested ternary
- `or []` / `or {}` inside a comprehension
- Unpacking and discarding a field (`for tf, _why`)
- A magic token (`"?"`, `0`) whose meaning is not a named constant on that line
- Lambda default-args used to freeze loop values (`lambda d=done: …`)

Do not narrate `x = x + 1`.

### Lessons-learned patches (redundant on purpose)

When code exists because of a fix documented in [Lessons_Learned.md](Lessons_Learned.md) or [Chart_Reveal_Invariants.md](runbook/Chart_Reveal_Invariants.md):

1. Add a **one-line comment at the top of the function or guarded block** stating the lesson in plain English (the failure mode and the rule). Example: `# Lesson: Plotly relayout drops title.text when only title.font is patched — restore text from STOCK_CHART_TITLE.`
2. Keep the central doc entry in the **same commit series** — code comment plus Lessons_Learned (or invariant doc) together.

The duplication is intentional: the next reader sees the rule in the file without opening docs; docs remain the canonical cross-session record.

---

## Rule of Three

Applies to **helpers**, **literals**, **repeated magic values**, and the **same bundle of facts** threaded through many functions — not only long functions.

| Count | What to do |
|-------|------------|
| **Once** | Fine inline — **except** paths, URLs, file names, hosts, ports, and other values that will change ([Do not hardcode](#do-not-hardcode-values-that-will-change-allen-lock)). |
| **Twice** | Duplication is OK for tiny snippets (about 1–2 lines) or one-off literals. |
| **Three** | Strong signal to centralize (shared helper, named constant, or **named instance**). |
| **Four or more** | **Must** be a named constant, helper, or class, scoped **as closely as possible** (function → module → package). Do not leave the same string/number/tuple copy-pasted. |

If centralizing **adds net lines to callers** without shrinking the overall codebase, it is probably over-engineered. Refactors should make call sites shorter and clearer.

### Same thing across functions → a named instance

When you keep talking about **the same thing** across a stretch of functions — the same entity + window + mode as parallel kwargs, a fat tuple, or a dict you unpack at every hop — that thing should be **real**: a class (or frozen dataclass) with a one-line purpose. Callers pass **one instance**.

Count still follows the table. Third copy of the same bundle is the extract. GUI widgets are this in the UI domain. Identity / DB-parity types live under the app’s domain package. Live run state lives on session objects. Do not paper over the extract with leftover `@property` names (see Files).

### Literals and enterprise scale

- **This project (and other small apps):** Rule of Three / Four is enough — named constants near the use site, or module-level constants. No need for a full i18n string catalog.
- **Enterprise / multi-language product:** the same literals eventually leave code entirely (resource files, message catalogs, config) so languages and ops can change text without a redeploy. Do **not** build that machinery here until the product needs it; do **not** keep scattering the same English string past the fourth copy either.

## Cohesion pairs (delete-together)

When placing or moving code, ask: **if this is deleted, what else must go with it?** Keep those pieces in one package (or one obvious pair) so the next agent does not leave orphans.

| Pair | Live together | Why |
|------|---------------|-----|
| SQL text + loader | `src/database/sql/*.sql` + `src/database/sql/loader.py` | Loader exists only to read those files; no `sql_loader.py` outside the folder. |
| Domain type + table DDL | `src/domain/` + matching `sql/*.sql` when introduced | Parity stays discoverable. |

### SQL lives in files (hard rule)

**Do not** leave SQL as Python string literals in application code (stores, reports, workers) — **including one-liners**. SQL changes over time; keep it in `.sql` files so the text can be edited and reviewed. Put every static statement in `src/database/sql/*.sql` (or `db/` migration/delta when it is a schema change) and load it with the SQL loader (`load_named_sql` / `load_sql`).

| Own | Where |
|-----|--------|
| **Statement text** | Schema, indexes, upserts, and report queries as `.sql` files |
| **Python store / UI** | Call the named statement, map rows, handle errors — not invent SQL strings in-line |

**Allowed exceptions (narrow):** only SQL that **cannot** be a static file — e.g. identifier quoting via psycopg `sql.Identifier` / `sql.SQL`, or a WHERE clause assembled from a fixed allow-list of fragments with a file template (`__WHERE__`). User or config text must never be concatenated into SQL.

**Loader duties:** resolve paths only under `sql/` (no traversal); sanitize human-edited files (encoding, BOM, nulls, empty); **cache** file text after first read. **Preload** (`preload_sql_files`, once per process on schema ensure): one **CODE** start/end pair for the batch — no per-file lines. **Execute** (`log_sql_execute`): tag **SQL** (level 15, between DEBUG and INFO) with file name + redacted binds. Visible at Log Level **DEBUG** or **SQL**, not at **INFO**. Never log the application_log insert itself (recursion).

**Why:** Reviewers can see and change queries without spelunking Python. One-liners drift just like multi-line blocks.

**Rules**

1. **Colocate dependents** — a helper that only serves one directory belongs in that directory (or package `__init__` re-export), not a sibling “misc” module.
2. **No permanent shims** after a move finishes (see Shims below).
3. **Update README Architecture** when the pair’s path changes.
4. **Update Project Hierarchy** when the **directory tree** or **Project window tabs** change (see below).


## Spreadsheet-style call sites

When the same function is called repeatedly with different parameters, prefer a compact table of calls over copy-pasted logic. Example: scale options, watchlist operations, or batch export steps.

If that table grows past **~5 rows**, or you are about to add the **third** block of the same shape, move the parameters into a metadata file (JSON/config) and load them at runtime. **Over ~10 rows:** do not keep growing `ScaleOption(...)` / parallel dicts in source — load from metadata and keep code as the loader + generic API.

## Centralized error handling

Do **not** duplicate error formatting or recovery hints in CLI, UI, and batch paths. Map exceptions in **one place** and reuse:

- CLI (`main.py`) logs the formatted message.
- UI (`stock_ui.py`) maps the same view to status labels and dialogs.

Changing error text or hints should require editing a single module.

### External API / network call errors — be as detailed as possible

When wrapping **Schwab**, Postgres drivers, HTTP clients, or any remote service:

| Do | Don’t |
|----|--------|
| Include **HTTP status** (or driver SQLSTATE / error code) in the exception message | Collapse every failure to “auth failed” or “request failed” |
| Surface vendor **title/detail** (Schwab `errors[].title` / `detail`) when present | Swallow the body and invent a vague label |
| Choose **distinct recovery hints** by cause (token expiry vs `Client not authorized` vs invalid_client vs 403 consent) | Always say “re-auth” for every 401 |
| Log the full message **and** `hint` at WARN/ERROR; show both on the active UI surface | Log a short string and hide the actionable fix |
| Redact secrets (tokens, auth headers) before message/hint/audit | Dump raw OAuth tokens into log or status bar |
| Prefer one mapper (`error_from_response`, `format_operation_error`) so all call sites stay detailed | Copy-paste thin `except` blocks that strip context |

**Why:** Market Data can succeed while Accounts/Trading returns `401 Client not authorized`. A generic “authentication failed” sends the user to re-login forever. Detail is how you separate product access, consent, credentials, and true token expiry.

**Audit path:** remote calls that go through `_call_with_token_refresh` already land in `api_transaction_audit` with `http_status` + redacted payload. User-visible messages must not be *less* informative than that row.

**Checklist when adding a new external call:**

1. Raise via the shared mapper (or extend it) — never bare `raise RuntimeError("failed")`.
2. Message includes operation context + status + vendor detail.
3. Hint names the next human step (portal product, reauth, network, schema).
4. Caller logs `exc` and `getattr(exc, "hint", None)`; UI status/dialog can show both.


## Boot-up and environment (try / catch, portable machines)

Boot paths run **before** the product is usable: interpreter choice, `.env`, Qt plugins, Postgres connect, Schwab tokens, schema ensure, SQL log handler, WebEngine process path. They fail differently on every machine (wrong conda env, IDE-polluted `QT_*`, missing `qwindows`, DB down, no tokens).

**Rule:** every boot step is **documented, try/caught, and reported with a meaningful next action** — not a native OS dialog, bare crash, or silent hang. Code that only works on Allen’s laptop is incomplete.


### Required pattern

1. **Isolate the step** in a named function or early `main` / launcher block (not buried mid-feature).
2. **try / except** around the step (or a helper that returns `None` / Result and never raises a raw plugin dialog into the user’s face from unit tests).
3. **Log** with enough context to fix it on a **new machine**: what ran, which path/env/interpreter, what failed, what to do next.
4. **Surface** a short human message (CLI stderr, status label, or dialog) — not only a stack trace.
5. **Document** the failure mode when you discover it: comment at the guard, [Lessons_Learned](Lessons_Learned.md) if non-obvious, runbook if operators need a ritual (`docs/runbook/Interactive_Charts.md` for Qt).

| Do | Don’t |
|----|--------|
| `bootstrap_qt_paths()` **before** any `QApplication` / PyQt import that needs plugins | Bare `QApplication([])` in tests or scripts and hope the OS has plugins |
| `try_create_qapplication()` (or equivalent) → skip/exit with “use trading_env / run_stock_data.ps1” | Let Windows show **“no Qt platform plugin could be initialized”** with no path hint |
| Override bad IDE/`QT_PLUGIN_PATH` / kill sticky `QT_QPA_PLATFORM=offscreen` from agent shells | `setdefault` that keeps an empty PyQt6 plugins tree |
| Include `sys.executable`, plugin root tried, and `QT_*` when logging Qt boot failure | Log only `Exception: failed` |
| Map DB/Schwab boot failures through existing mappers + hint | Hang on “Loading…” with no log and no status change |
| Prefer **trading_env** via `PYTHON_PATH` / `./run_stock_data.ps1` | Default base Anaconda on PATH for UI or Qt unit tests |

### Tests and agents

- Unit tests that need a real `QApplication`: call **`try_create_qapplication()`**; if `None`, **`pytest.skip`** with the fix hint — never pop a native platform dialog.
- Agents and CI must not leave `QT_QPA_PLATFORM=offscreen` in a shell that later launches the desktop UI without re-bootstrap.
- Smoke / UI launch: `./run_stock_data.ps1` (clears polluted `QT_*`, sets conda plugin path, then `main.py`).

### When you add a new boot step

Checklist (same spirit as external API errors):

1. Named helper or obvious call site in launcher / `main` / first use.
2. try/catch or Result; no uncaught native dialog for expected env mistakes.
3. Message names the **machine-local fix** (interpreter, `.env` key, install plugin, start Postgres).
4. One sentence in Coding_Standards, Lessons, or the relevant runbook if this failure will recur on migrate.
5. Prefer reusing `bootstrap_*` / `try_*` helpers over a third copy of path logic.

**Why:** Moving Stock_Data to another PC is normal. Boot failures are the first thing the new machine hits. Graceful, greppable, actionable errors are part of the product — not “works on my box.”

### Busy cursor (hourglass)

Any user-visible work that may take more than a blink (DB load, statement recompute, Schwab history backfill, multi-account paint) must show a **wait cursor** so the app does not look frozen.

| Do | Don’t |
|----|--------|
| Named owner: `StockUI._busy_acquire("acct_history_paint")` / `_busy_release(...)` (refcount-safe) | Bare `setOverrideCursor` without matching restore |
| Panel `set_busy(True)` that sets **WaitCursor** + disables primary action | Busy only on Refresh while range change / paint still blocks |
| **`try` / `finally`** always release | Leave WaitCursor stuck after exception |
| Status text: what is happening (“Loading statements / daily closes…”) | Silent multi-second UI freeze |
| Neighbor **prefetch** stays LED-only — **never** takes the hourglass (ADR 0001 / dual paint) | Gate symbol change on hourglass forever |

New heavy paths (import scripts run off-UI; long UI jobs still hourglass). Prefer worker thread + busy for multi-second network; still hourglass while the UI thread awaits result.

## User input settling time (debounce)

Give the user time to finish a gesture before firing expensive work (chart reload, prefetch, DB/API fetch). Use a **named constant** and a **single-shot `QTimer`** that restarts on each event — do not hard-code magic milliseconds at call sites.

**Qt timers:** only the window thread constructs `QTimer`. Workers marshal with a queued helper (`ui_single_shot` or equivalent). Do not parent a timer to a GUI widget from a worker, and do not fall back to running the callback on the worker when marshal fails.

## UI thread vs data (MVC)

The paint / mouse thread never runs date searches, hole scans, or store/SQL. It reads domain objects and DataFrames already in memory. Workers populate those objects. A presenter may **submit** work and **apply** the result.

| Layer | Job |
|-------|-----|
| **Model** | Persist and retrieve rows. SQL in files. |
| **Domain** | Turn frames into meaning. Populate what the UI will read. |
| **View** | Paint and clicks. Never issue a data call. |

A database change stays in the model. The UI keeps the same bundle.


### Attention chrome (user needs to look here)

Shared module: [`src/ui/attention_style.py`](../src/ui/attention_style.py). Use for **any** control that needs attention without a modal.

| Level | Color | Typical use |
|-------|-------|-------------|
| **none** | default | Condition cleared (valid field, re-auth done) |
| **warn** | **yellow**/amber border or tab text | Soft deadline (e.g. Schwab re-auth **≤ 48 hours**) |
| **urgent** | **red** border/label/tab text | Hard deadline or invalid draft (e.g. re-auth **≤ 24 hours**, blank Range) |
| **changed** | **green** text | Unsaved Settings Value (clears on Save / Discard) |

| Do | Don’t |
|----|--------|
| `set_widget_attention(widget, level, tooltip=…)` / `set_tab_attention(tabs, index, level)` | One-off red styles scattered per feature |
| Tooltip explaining **what** and **where** | Modal/popup for intermediate or soft deadlines |
| Clear to **none** when resolved | Leave yellow/red after success |
| **Be patient** on blank required fields — no apply until valid | Coerce empty → min and thrash the chart |
| Keep last valid product state while drafting | Blank the graph to “force” the user |

## Shims (transitional only)

Allen accepts shims **only as a short bridge** during an import-path move. When a refactor finishes, the tree should be **clean** — canonical modules, no duplicate bodies, no permanent re-export files.

| Rule | Detail |
|------|--------|
| **When** | Only when deleting or moving a module would break the app mid-refactor. |
| **Shape** | One thin file: docstring, handoff comment, single `from canonical import *` (or explicit re-exports). **Never** leave the old module body below the shim. |
| **Finish** | `rg` shows no imports of the old path → delete shim → smoke tests → commit. |
| **Owner** | If a shim lists Grok Build in its handoff comment, do not extend it — complete the migration instead. |

See also shim-removal items in [ToDo.md](ToDo.md).

## Testing: unit / smoke / integration / regression vs probes

**How to write a test:** [tests/README.md](../tests/README.md) and [PROCESS.md](PROCESS.md) § Tests. That is the day-one duty (a test with every change, isolation, GUI windows, capture on adoption). The rows below name the buckets. GitHub Actions, pytest-testmon, and canaries stay dormant until the unfold pick.

| Kind | Path | Rule |
|------|------|------|
| **Unit** | `tests/unit/` | Inputs in, outputs match. No database, no network, no real window. |
| **Smoke** | `tests/smoke/` | Key components work: the app boots and reaches the important places (external services, database, each core feature). Early warning before production users. A real local service belongs here. |
| **Integration** | `tests/integration/` | The whole app from the start through key parts. Generally the happy path. |
| **Regression** | `tests/regression/` | The edge cases. |
| **Probe** | `scripts/experiments/`, local `_probe_*` | Debug one issue; **do not commit** scratch under `scripts/testing/_probe_*` (gitignored). |
| **Harness** | `scripts/testing/run_smoke_suite.py` | Thin pytest facade (`--tier` → paths); no business logic. |

**Rules:** New tests go under `tests/{unit,smoke,integration,regression}/` as `test_*.py` with `test_*` functions. Run in that order and stop on the first failing tier. Pytest exit 5 (no tests collected) counts as pass. Path auto-marks the bucket in [tests/conftest.py](../tests/conftest.py). Config/markers: [pyproject.toml](../pyproject.toml).

**Hierarchy compliance (required):** Maintain pytest as the canonical test hierarchy. `tests/unit`, `tests/smoke`, `tests/integration`, and `tests/regression` are the durable homes for committed behavior checks. Keep names/markers pytest-compliant and keep test intent aligned with the bucket (unit = function in, outputs match; smoke = key components work, early warning; integration = happy path from the start; regression = edge cases).

**Script-test migration rule:** Most script-style tests should live in `tests/` instead of `scripts/`. Keep `scripts/testing/` focused on orchestration wrappers (for example `run_smoke_suite.py`), one-off local probes, and short transition helpers. If a script asserts product behavior more than once, promote it to pytest under the proper hierarchy.

Pre-push default: `python scripts/testing/run_smoke_suite.py` (runs `pytest tests/unit`) or `pytest tests/unit`. Promote a probe into `tests/` when the assertion should never regress. See [scripts/testing/README.md](../scripts/testing/README.md).

## Refactor workflow

1. Work in **logical layers** (data → client → UI, not everything at once).
2. **Smoke-test** after each layer (`run_smoke_suite.py --tier fast`; add `db`/`live` when the layer touches Postgres or Schwab).
3. **Commit** each layer separately.
4. **Push** only when the full refactor is reviewed and complete.

### Pre / post performance (hot paths)

When a refactor **moves or rewrites code the user waits on** (paint, poll, fetch, DB load) — or any path that already has a hitch/latency budget:

1. **Name the set.** A short list of cases that exercise the functions you will move — not the whole suite. Keep it next to the code (`tests/…/bench_*.py` plus a `scripts/testing/bench_*.py` runner).
2. **Run twice before edits.** Two consecutive runs on the same machine, same args. The two runs must **agree on the pattern** (same case order; no case swinging by ~2×). If they disagree, fix the bench (warmup, Qt, disk) **before** you cut code.
3. **Record** median milliseconds per case (chat summary + Change_Log **Details**).
4. **Change the code.**
5. **Run the same set after.** Once is enough when it matches the pre pattern; twice if the first post look is off.
6. **Compare.** Stay under the named hitch budgets. A slowdown that still fits the budget: note it. A miss vs budget or a large regression vs pre: **SHORTFALL** in that turn — do not ship as “just a split.”

Skip this for docs-only, rename-only, or comment-only changes. This does **not** replace dual paint+prefetch fences.

## What to leave alone

- Focused single-purpose modules that are already short.
- UI-only presentation (charts, logos, layout) — unless the **file** crosses the ~500-line threshold *and* a real seam exists (see **Files**).
- One-off scripts that are not duplicated elsewhere.

## Agent checklist

Before finishing a task (feature, fix, or refactor) — code **and** docs:

**Code**

- [ ] Slice is **as good or better** than when we started (bugs, speed, clutter, reliability). Knowingly worse does not ship ([Taste.md](Taste.md) **Leave the code better**).
- [ ] Net line count at call sites went down (or stayed flat with real duplication removed).
- [ ] No third copy of the same 3+ line block remains.
- [ ] No third copy of the same kwargs/tuple/dict bundle across functions — that bundle is a named class (one instance), not more kwargs.
- [ ] Errors route through the shared formatter.
- [ ] New/changed classes and major functions have a one-line purpose comment.
- [ ] Dense one-liners have a why-comment. Split only when a straightforward comment cannot name what the line does.
- [ ] New/changed imports have inline purpose comments.
- [ ] No new **file** approaches 500 lines without a split plan (or a documented “leave whole” reason from **Files**).
- [ ] Smoke tests pass (`run_smoke_suite.py --tier fast`; add `db`/`live` when relevant).
- [ ] Hot-path refactor: named benchmark run **twice before** and **once after**; pre/post recorded; no hitch-budget miss without a **SHORTFALL**.
- [ ] No new permanent shims; any temporary shim has a removal path in ToDo or the PR plan.
- [ ] After a collaborator extract: remaining call sites retargeted and old `@property` names **deleted** in the same series (leftover-name aliases only if the app would otherwise fail to run).
- [ ] No new warning squelch (filter/collapse/demote stderr or “ignore WARN”); root cause fixed or process re-engineered (see **Warnings are almost always a deeper problem**).
- [ ] No new hardcoded path, URL, runtime file name, host, or port in product code (see **Do not hardcode**). Value is `.env` / config or derived.

**Documentation** (same commit series as code — see [PROCESS.md](PROCESS.md) §3 and [AGENTS.md](../AGENTS.md))

- [ ] **Change summary** written for the human ([PROCESS.md](PROCESS.md) § Handoff to human). When the session finishes: `git switch main && git pull --ff-only`; if the diff is worth keeping, branch off that `main`, squash-merge, delete the local and remote branches; `grok worktree rm <id>` if a managed worktree was used ([PROCESS.md](PROCESS.md) § Parallel sessions).
- [ ] [Change_Log.md](Change_Log.md) row when behavior, schema, or user-facing output changed (**Why** / **What** / **Benefit**; **Shot:** when a tab/chrome paint changed — PROCESS § Change_Log screenshots).
- [ ] [ToDo.md](ToDo.md) whenever the task involved an open ToDo item — completed parent block → [ToDo_Completed.md](ToDo_Completed.md); new work → open item added. **Required if ToDo was in scope;** not optional.
- [ ] This file **only** when a new **rule** or workflow norm changed — **not** for small bug fixes or routine features.
- [ ] [Lessons_Learned.md](Lessons_Learned.md) when diagnosis was non-obvious or surprised us.
- [ ] [README.md](../README.md) Project Structure / Architecture when paths or module map changed.

**Git**

- [ ] Commit message ends with `Assisted-by: Grok Build` or `Assisted-by: Microsoft Copilot` (see [AGENTS.md](../AGENTS.md)).
- [ ] PowerShell-safe commit form (`-m` / `-F`); verify with `git log -1 --format=%B` before push.
