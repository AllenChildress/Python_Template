# Template inheritance

How this repo sits in the chain, and how a child takes parent changes.

Nothing in the chain updates by itself. There is no GitHub Action, bot, or submodule that moves code downstream. A person (or an agent the person asked) merges on a branch and opens one pull request. Allen approves that PR. One repo, one PR.

## The chain

```text
LLM_Project_Template  →  Python_Template  →  Python projects
(staff kit)              (this repo)          Stock_Data
                                              Option_Chain_Logger
                                              new Python apps
```

| Repo | Job | Parent remote |
|------|-----|----------------|
| [LLM_Project_Template](https://github.com/AllenChildress/LLM_Project_Template) | Language-agnostic staff kit: process, agents, docs hygiene, test layout, logging norms | none |
| [Python_Template](https://github.com/AllenChildress/Python_Template) | Permanent Python layer. The staff kit, plus shared Python behavior (the metadata CSV loader, `running_under_tests`) | `https://github.com/AllenChildress/LLM_Project_Template.git` |
| Stock_Data, Option_Chain_Logger, and each new Python app | Product code | `https://github.com/AllenChildress/Python_Template.git` |

The split exists so a process fix and a Python-loader fix each have one home. Product repos stay product repos. A kit change is merged down; it is not retyped into each app.

## How a child pulls parent changes

Do this in the **child** repo. `upstream` is the parent. `origin` stays the child.

One time:

```bash
git remote add upstream https://github.com/AllenChildress/LLM_Project_Template.git
```

Python projects use Python_Template’s URL instead:

```bash
git remote add upstream https://github.com/AllenChildress/Python_Template.git
```

`git remote -v` shows whether `upstream` is already there. Add it once.

Each time the parent has something worth taking:

```bash
git fetch upstream
git switch main
git pull --ff-only origin main
git switch -c sync/upstream-main
git merge upstream/main
```

Resolve conflicts by hand with the ownership list below. Open a pull request into the child’s `main`. Allen approves it. The usual land step squash-merges after that approval. Do not merge it from the parent repo, and do not turn on auto-merge.

A later merge is the same commands. After the first successful merge, history is related, so `git merge upstream/main` is a normal merge.

### First merge: unrelated histories

GitHub **Use this template** copies the files and starts a **new** commit. The child does not share history with the parent. Stock_Data and Option_Chain_Logger were not created from Python_Template, so they do not share history with it either.

The first merge in those repos needs:

```bash
git merge upstream/main --allow-unrelated-histories
```

Git will treat every file as a conflict or as a new file. Resolve them by hand. Do not pass `-X ours` or `-X theirs`. After that PR is merged, drop the flag. The next `git merge upstream/main` is a normal merge.

This repo (Python_Template) was created from LLM_Project_Template with Use this template. Its own first catch-up from that parent uses the same flag.

## Which files are whose

The list in this file is the authority. A marker on the first line is a hint so a conflict is obvious:

| Marker | Meaning |
|--------|---------|
| `<!-- template-owned: LLM_Project_Template -->` or `# template-owned: LLM_Project_Template` | Parent kit. Take the parent’s version. |
| `<!-- template-owned: Python_Template -->` or `# template-owned: Python_Template` | Python layer. Python projects take this repo’s version. |
| `<!-- python-layer: Python_Template -->` … `<!-- /python-layer -->` | A Python-layer passage inside a parent-kit file. Keep the passage when the parent file is merged. |
| `<!-- project-owned -->` or `# project-owned` | The child owns it. Keep the child’s version. |

On a conflict:

1. Template-owned path: take the parent that owns it, then put back any fenced passage this list says to keep.
2. Project-owned path: keep the child’s version.
3. Shared path: keep both intents. Rules for those files are in the shared table.

### Parent kit (LLM_Project_Template)

Take the parent’s version. Python_Template does this when it merges the staff kit. Python projects receive these files by merging Python_Template (which already carries them).

- `docs/PROCESS.md`
- `docs/Coding_Standards.md` (keep the fenced **Non-user tuning** section and the metadata sentence under Spreadsheet-style call sites)
- `docs/Taste.md`
- `docs/Libraries.md` (keep the fenced sentence that points tuning at the metadata CSV)
- `docs/Database.md` (keep the fenced sentence that points tuning at the metadata CSV)
- `docs/changelog_shots/README.md`
- `docs/skills/README.md`, `docs/skills/Domain/README.md`, and `docs/skills/General/` when that folder exists
- `.grok/skills/`
- `tests/conftest.py`, `tests/window_policy.py`, `tests/README.md`
- Kit tests: `tests/unit/test_window_policy.py`, `tests/unit/test_run_tiers.py`, `tests/unit/test_capture_output.py`, `tests/unit/test_promote_changelog_shot.py`, `tests/unit/test_regression_marker.py`
- `scripts/run_tiers.py`, `scripts/score_cc.py`, `scripts/promote_changelog_shot.py`, `scripts/capture_changelog_tabs.py`, `scripts/capture_console_text.py`, `scripts/capture_output.py`, `scripts/README.md`
- `.vscode/extensions.json`

`docs/Lessons_Learned.md` sections **Grok multi-session**, **Tests**, **General**, **Environment**, and **Windows executable packaging** are parent kit. The **Template chain** section is Python-layer: keep it. The **Domain / product** section is project-owned.

`docs/Glossary.md` starter rows are parent kit. The **Python layer** section is Python-layer: keep it. Product rows a child adds are project-owned.

### Python layer (this repo)

Python projects take this repo’s version.

- `docs/Template_Inheritance.md`
- `docs/Metadata.md`
- `src/metadata_settings.py`
- `src/runtime_flags.py`
- `tests/unit/test_metadata_settings.py` (see the sample-row note below)
- `tests/unit/test_runtime_flags.py`
- `metadata/settings.csv` **header row** (`category,variable,value,updated,description`)

Data rows in `metadata/settings.csv` are project-owned. This repo ships two examples. A project replaces those rows with its own tuning and, in the same PR, rewrites `test_python_template_sample_rows` so it still matches the file. On a later merge, keep the child’s data rows and that one test’s assertions, and take the parent’s header and the rest of the test file.

`metadata/local/` is gitignored. It is never a merge input. The app may write it. Nobody commits it.

### Project-owned

Keep the child’s version.

- Product packages and modules other than `src/metadata_settings.py`, `src/runtime_flags.py`, and a marker-only `src/__init__.py`
- `docs/skills/Domain/` playbooks the app adds (the empty README stays the kit’s)
- App schema, SQL, and runbooks
- `.env` (never committed) and the product keys in `.env.example` below the project-owned marker
- `docs/ToDo.md` (each repo’s backlog)
- `metadata/local/`

`src/__init__.py` in this repo is a package marker. A child that already has a package init keeps the child’s file. The two Python-layer modules still import as `src.metadata_settings` and `src.runtime_flags`.

`AGENTS.md`: the session rules and the parallel-session rules are parent kit. The opening line that says product repos inherit the file is Python-layer: keep it. The **architecture paragraph** is project-owned (each repo describes itself). The Start-here rows for this file and for [Metadata.md](Metadata.md) are Python-layer: keep them. The checklist sentence that sends non-user tuning to the metadata CSV is Python-layer: keep it. The do-not-commit line for `metadata/local/` is Python-layer: keep it.

### Shared

| File | On a conflict |
|------|----------------|
| `README.md` | Keep this repo’s opening description (it names the parent). Take parent edits to environment setup and extensions. Keep the layout lines for `metadata/` and `src/metadata_settings.py`. |
| `Project.md` | Keep the intake answers the child wrote. Keep the **One config story** row that points tuning at the metadata CSV. |
| `docs/Change_Log.md` | Keep every entry from both sides, newest first. Do not drop a parent kit row or a child product row. |
| `.gitignore` | Keep kit entries and the `metadata/local/` line. Keep extra app entries below a `# project-owned` marker. |
| `.env.example` | Keep kit keys and the opening comment that points tuning at the CSV. Keep app keys below the project-owned marker. |
| `metadata/settings.csv` | Keep the template header. Keep the child’s data rows. |

## Create a new Python project

1. On GitHub, open [Python_Template](https://github.com/AllenChildress/Python_Template) and choose **Use this template**. Name the new repo.
2. Clone the new repo.
3. Add the parent remote once: `git remote add upstream https://github.com/AllenChildress/Python_Template.git`.
4. Fill the architecture paragraph in `AGENTS.md`, answer [Project.md](../Project.md) intake, and replace the sample rows in `metadata/settings.csv` with this project’s tuning. Update `test_python_template_sample_rows` in that same change.
5. When this repo later has commits the child needs, follow [How a child pulls parent changes](#how-a-child-pulls-parent-changes). The **first** merge uses `--allow-unrelated-histories`.

## One-time catch-up for Stock_Data and Option_Chain_Logger

Those repos were not built from Python_Template. They already have product history. Catch-up is one PR in each repo, not a rewrite.

1. In that clone, `git remote add upstream https://github.com/AllenChildress/Python_Template.git`.
2. `git fetch upstream`.
3. Branch from that repo’s current `main`.
4. `git merge upstream/main --allow-unrelated-histories`.
5. Resolve by the tables above. Product modules, Change_Log product rows, and ToDo stay. Python-layer files arrive. The metadata header arrives; the project’s tuning rows are the data rows (the two examples here are not that app’s settings).
6. Open one PR. Allen approves it.

After that PR merges, later pulls are a normal `git merge upstream/main`.

This document does not name origin URLs for Stock_Data or Option_Chain_Logger. Add `upstream` in the clone you already have.
