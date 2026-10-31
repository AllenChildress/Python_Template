# Project — staff kit spine

**Purpose:** One file to drop into (or copy from) a new VS Code project so Grok Build and humans share the same expectations. Framework for robust application development — not product domain content.

**How to use with an agent**

1. Paste or open this file.
2. Answer **§ Intake** (or use multi-choice prompts if the agent offers them).
3. Ask: *“Implement the staff kit for this repo based on my intake answers and the stubs under docs/.”*
4. Agent fills templates, skips declined sections, writes a short Change_Log row for the bootstrap.

---

## Intake (ask the developer)

Copy answers under each line or reply in chat.

### Product

- [ ] App name / one-sentence purpose: _______________
- [ ] Primary language(s): _______________
- [ ] UI? (none / CLI / desktop / web): _______________
- [ ] Database? (none / SQLite / Postgres / other): _______________
- [ ] External APIs / auth?: _______________

### Kit modules (include?)

| Module | Include? | Notes |
|--------|----------|--------|
| AGENTS.md | Y / N | Session rules. Nested files are folder reading lists |
| PROCESS.md | Y / N | Always recommended |
| Coding_Standards.md | Y / N | Always recommended |
| Change_Log.md | Y / N | User-visible history |
| Glossary.md | Y / N | Shared words |
| ToDo.md (+ Done) | Y / N | Backlog |
| Lessons_Learned.md | Y / N | Scar tissue |
| Taste.md | Y / N | Judgment |
| Logging norms | Y / N | Levels / story vs construction |
| tests unit/smoke/integration/regression | Y / N | Run in that order; stop on the first failing tier |
| pytest + suite script later | Y / N | |
| CI / pytest unfold (dormant) | Y / N | GitHub Actions + canaries + testmon **off** until PROCESS threshold, then one purple pick |
| Screenshot smoke (UI apps) | Y / N | |
| DB schema + migrations pattern | Y / N | See [docs/Database.md](docs/Database.md) |
| Backup script pattern | Y / N | |
| Recommended libraries list | Y / N | [docs/Libraries.md](docs/Libraries.md) |
| Domain skills folder | Y / N | Product-specific playbooks |

### Constraints

- Prefer short agent replies? Y / N  
- Commit message trailers (`Assisted-by: …`)? Y / N  
- Default: **do not push** until human asks? Y / N  

---

## Target file set (after intake)

```text
AGENTS.md
docs/PROCESS.md
docs/Coding_Standards.md
docs/Change_Log.md
docs/Glossary.md
docs/ToDo.md
docs/Lessons_Learned.md
docs/Taste.md                    # optional
docs/skills/General/…            # optional playbooks
docs/skills/Domain/…             # optional
tests/{unit,smoke,integration,regression}/
```

App-specific docs (schema, runbooks, product ADRs) stay **outside** this kit once the app grows.

---

## Skeleton rules (agent implements)

1. **Never load the whole docs set** into context — open only files named by AGENTS / task.
2. **One Change_Log entry per user-visible change** (Why / What / Benefit). If a view/tab paint changed, add **Shot:** (PROCESS § Screenshots).
3. **ToDo** updated when backlog items complete or cancel.
4. **Module size:** prefer files under ~500 lines; split by purpose (not arbitrary chops).
5. **Tests:** every feature or fix ships with a test (bug fix fails first). Adopting an app: unit tests for the core logic, a smoke check that key components work, and a capture script. See [tests/README.md](tests/README.md).
6. **Secrets:** never commit `.env`, tokens, dumps.
7. **Generic vs specific:** kit files stay portable; product truth lives in the app repo.

---

## Lightweight practices (solo / small team)

Enough structure to stay reliable — not a process theater.

| Practice | Why |
|----------|-----|
| **Main stays shippable** | Land work on short-lived branches (or sequential commits on solo work); avoid long-lived “mystery” branches. |
| **Definition of done** | Behavior works · relevant test · Change_Log/ToDo if user-visible · secrets still out of git. |
| **Read your own diff** | Before commit: `git status` + diff; agents still need a human sanity check. |
| **Lock dependencies** | Commit `requirements.txt` or lockfile; recreate envs from the file, not “whatever was on the machine.” |
| **One config story** | `.env` / env vars for secrets and local paths; document required keys in `.env.example` (no values that matter). |
| **Backup before destructive DB** | `pg_dump` (or equivalent) before migrations that drop or rewrite data. |
| **Keep AGENTS architecture current** | One paragraph that matches the real stack beats a stale essay. |
| **Handoff note** | Short: what changed · how to verify · push status (local until asked). |

Skip formal sprint ceremony, mandatory PR templates, and multi-page ADRs until the team or risk actually needs them.

---

## Public sharing / demos (careful)

| Usually OK | Avoid |
|------------|--------|
| Staff kit (this repo) | Secrets, tokens, `.env` |
| Generic UI / architecture demos | Live production data, PII, credentials |
| Architecture diagrams | Account numbers, emails, API keys in cleartext |
| Redacted process docs | Full personal Change_Log dumps with private detail |

Crop screenshots that show private identifiers. Prefer sample or synthetic data when presenting.

---

## Meetup talk track (optional agenda)

Use this kit as the demo spine (not a specific product’s internals).

1. Grok Build in VS Code + GitHub  
2. Skill / staff files: AGENTS, PROCESS, Coding_Standards  
3. Documentation: Change_Log, Glossary  
4. Logging  
5. Testing (unit, smoke, integration, regression, in that order; pytest, screenshots)  
6. Database (schema, migrations, backups) — if included  
7. Data model (session-style ownership over map sprawl) — if applicable  
8. UI patterns (tabs, status, refresh, log) — if applicable  
9. Performance (caching, honest limits of UI stacks)  
10. Self-assessment prompts (prompts on *prompts* and on *Change_Log*)  
11. Parallel work (agents + language threads — different tools)  
12. Cost / ROI (fill your own numbers)

---

## Self-assessment prompts (exercises)

**#1 — Prompts:**  
*Looking at my prompts, what can you tell me about the type of programmer I am, my style, experience level, and areas for improvement?*

**#2 — Change_Log:**  
*Looking at Change_Log.md, what can you tell me about the type of programmer I am, my style, experience level, and areas for improvement?*

---

## OOP analogy: kit vs app docs

| Layer | Role | Example |
|-------|------|---------|
| **Base (this kit)** | Portable process | “Always keep a Change_Log” |
| **Subclass (app)** | Product instance | App’s long Change_Log, deploy runbook, domain skills |
| **Do not** | Merge product secrets into the kit | Tokens, customer data, vendor quirks |

When the app learns a **general** lesson, promote a short rule into this kit. When the lesson is **domain-only**, keep it in the app (or `docs/skills/Domain/`).

---

## Agent bootstrap prompt (copy-paste)

```text
Open Project.md and the stubs under docs/.
I answered intake as follows:
  <paste answers>

Implement the staff kit for this repository:
- Keep files portable (no personal secrets, no product-domain content).
- Skip modules I set to N.
- Fill placeholders; leave TODO comments where I must supply product names.
- Add one Change_Log entry for this bootstrap.
Do not push unless I ask.
```
