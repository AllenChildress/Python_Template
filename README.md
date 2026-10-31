# Python_Template — Python layer on the staff kit

**Python_Template** inherits from [LLM_Project_Template](https://github.com/AllenChildress/LLM_Project_Template). The parent is the language-agnostic staff kit: process, agents, docs hygiene, testing layout, and logging norms. This repo is the permanent Python layer in the chain. Python projects such as Stock_Data and Option_Chain_Logger inherit from here.

```text
LLM_Project_Template → Python_Template → Python projects
```

Changes move down the chain. A child adds the parent as an `upstream` remote, merges on a branch, and opens one pull request. Allen approves that PR. Nothing updates automatically. Steps, the first-merge flag for a repo created with GitHub “Use this template,” and which files are template-owned: [docs/Template_Inheritance.md](docs/Template_Inheritance.md).

Non-user tuning lives in one checked-in CSV, [`metadata/settings.csv`](metadata/settings.csv). Secrets and the few values a person really changes stay in `.env`. Pattern: [docs/Metadata.md](docs/Metadata.md).

**Not** a product application. A Python layer projects inherit, for solo or small-team work.

| Audience | Use |
|----------|-----|
| **You** | Create a Python repo with GitHub “Use this template” on this repo, or catch an existing repo up once ([docs/Template_Inheritance.md](docs/Template_Inheritance.md)). Then answer intake in [Project.md](Project.md). |
| **Small team / meetup** | Share as “how we run agent-assisted projects.” |
| **Grok Build** | Open *this* folder as the workspace to edit the kit without polluting app repos. |

## Quick start

1. Create the project with GitHub **Use this template** on this repo. Stock_Data and Option_Chain_Logger were not built from it; use the one-time catch-up in [docs/Template_Inheritance.md](docs/Template_Inheritance.md). The first merge from a parent uses `--allow-unrelated-histories`.
2. Install tools and extensions (see **[Environment setup](#environment-setup)** below). **Requires Grok Build 1.0.42 or newer.**
3. Open the folder in VS Code + Grok Build.
4. Read **[Project.md](Project.md)** — answer the intake questions (or paste them to the agent).
5. Agent implements from the stubs under `docs/` and root `AGENTS.md`.
6. Replace the architecture paragraph in `AGENTS.md` with this product, and delete intake sections you declined.

Requires Grok Build 1.0.42 or newer.
1.0.5 reclaims idle checkouts under `~/.grok/worktrees` when safe and never deletes the last copy.
1.0.19 adds `--worktree` to headless `grok -p`.
1.0.42 adds `grok worktree create` (managed worktree, no session).
A Grok worktree is a detached checkout at the base commit. It does not create a branch. Ending a session does not remove it. Land with ordinary git. Remove with `grok worktree rm` or `grok worktree gc --max-age 7d`.

Parallel Git rules: [AGENTS.md](AGENTS.md) § Parallel Session Rules and [docs/PROCESS.md](docs/PROCESS.md) § Parallel sessions. One writer, short task: stay in the primary checkout. A second writer uses a Grok managed worktree (`grok -w --ref main` / `grok worktree create`). This kit does not support older Grok Build for that path.

## Environment setup

### Core tools

| Tool | Install |
|------|---------|
| **Visual Studio Code** | [code.visualstudio.com](https://code.visualstudio.com/) |
| **Python 3.11+** (3.12 preferred) | [python.org/downloads](https://www.python.org/downloads/) — check “Add python.exe to PATH” on Windows |
| **Git** | [git-scm.com](https://git-scm.com/downloads) |
| **PostgreSQL** (if your app needs a server DB) | [postgresql.org/download](https://www.postgresql.org/download/) — [Windows installers](https://www.postgresql.org/download/windows/) · [macOS](https://www.postgresql.org/download/macosx/) · [Linux](https://www.postgresql.org/download/linux/) |
| **Grok Build (CLI)** | Official install: `curl -fsSL https://x.ai/cli/install.sh \| bash` — announcement: [Introducing Grok Build](https://x.ai/news/grok-build-cli). SuperGrok or X Premium Plus. On Windows, use a terminal that supports the installer, or follow xAI’s current platform notes after install. |

Python libraries for a given app go in that app’s `requirements.txt` / `pyproject.toml` after [Project.md](Project.md) intake. See [docs/Libraries.md](docs/Libraries.md) for a starter menu (`pip install …` or `uv` / Poetry). Never commit `.env` or `metadata/local/`.

### VS Code / Cursor extensions

Open **Extensions** (`Ctrl+Shift+X` / `Cmd+Shift+X`), search by name, or use the Marketplace links. This repo also ships [`.vscode/extensions.json`](.vscode/extensions.json) so VS Code can prompt you to install recommendations.

| Extension | Why | Marketplace |
|-----------|-----|-------------|
| **Grok Build for VS Code (Community)** | Sidebar UI over the Grok Build CLI | [PawelHuryn.grok-vscode-phuryn](https://marketplace.visualstudio.com/items?itemName=PawelHuryn.grok-vscode-phuryn) |
| **PowerShell** | Integrated terminal scripting on Windows | [ms-vscode.PowerShell](https://marketplace.visualstudio.com/items?itemName=ms-vscode.PowerShell) |
| **Python** | Language support, run/test integration | [ms-python.python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) |
| **Python Debugger** | Breakpoints, step-through (`debugpy`) | [ms-python.debugpy](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy) |
| **Python Environments** | Create / switch envs and packages | [ms-python.vscode-python-envs](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs) |
| **TODO.md Kanban Board** | Visual board backed by a portable `TODO.md` | [coddx.coddx-alpha](https://marketplace.visualstudio.com/items?itemName=coddx.coddx-alpha) |

**Command-line install (optional):**

```powershell
code --install-extension PawelHuryn.grok-vscode-phuryn
code --install-extension ms-vscode.PowerShell
code --install-extension ms-python.python
code --install-extension ms-python.debugpy
code --install-extension ms-python.vscode-python-envs
code --install-extension coddx.coddx-alpha
```

After installing Grok Build (CLI and/or extension), open this folder as the workspace and complete sign-in when prompted.

Postgres wiring after install: [docs/Database.md](docs/Database.md).

## Layout

```text
Python_Template/
  README.md                 # this file
  Project.md                # intake + skeleton + light practices
  AGENTS.md                 # session rules; nested files are folder reading lists
  .grok/skills/             # auto-loaded by Grok Build (e.g. git-workflow-and-versioning)
  .vscode/extensions.json   # recommended extensions
  metadata/
    settings.csv            # checked-in tuning; agents edit it in a PR
    local/                  # gitignored measured sidecar; the app may write it
  src/
    __init__.py             # package marker; a child with its own init keeps that file
    runtime_flags.py        # running_under_tests()
    metadata_settings/      # the only metadata CSV loader; import the package, not a sibling
      __init__.py           # public door: MetadataStore and the names callers use
      csv_table.py          # read the CSVs and merge the sidecar over the defaults
      getters.py            # typed int, float, str, and bool reads
      startup_log.py        # one startup line per loaded value
      sidecar.py            # measured writes and drift
      store.py              # MetadataStore, the object callers hold
      rows.py               # columns, paths, and row objects
  docs/
    PROCESS.md              # how work is done
    Template_Inheritance.md # chain, upstream merge, file ownership
    Metadata.md             # metadata CSV and the one loader
    Coding_Standards.md     # style, errors, **500-line hard cap**
    Change_Log.md           # user-visible history template
    Glossary.md             # shared vocabulary + common libraries
    Libraries.md            # recommended Python library menu
    Database.md             # Postgres vs SQLite vs Timescale; install sketch
    ToDo.md                 # backlog / Done
    Lessons_Learned.md      # durable scars (general section first)
    Taste.md                # judgment / “who is the computer”
    changelog_shots/        # tracked JPEG thumbs for Change_Log
    skills/
      README.md             # on-demand playbooks (not auto-loaded)
      General/              # portable playbooks
      Domain/               # empty — project-specific skills later
  scripts/
    README.md               # helpers (Change_Log thumbs, …)
    promote_changelog_shot.py
    capture_changelog_tabs.py  # GUI smoke capture — bind to your window
    capture_console_text.py    # console / TUI smoke capture
    capture_output.py          # gitignored capture folders
  tests/
    README.md               # how to write tests; run unit, smoke, integration, regression
    conftest.py             # maximize-on-one-screen; no-op without Qt
    window_policy.py        # pure screen / headless decisions
    unit/
    smoke/
    integration/
    regression/
  .gitignore
```

## Staff kit vs skills vs app docs

| Kind | What it is | Lives |
|------|------------|--------|
| **Staff kit** | How *any* project is run with humans + agents | Inherited from LLM_Project_Template; this repo carries it down the chain |
| **Auto-loaded skills** | Grok loads these on every session | `.grok/skills/` (and `~/.grok/skills/`) |
| **On-demand playbooks** | Paste/attach for a *task* (often domain) | `docs/skills/…` — this path is **not** auto-loaded |
| **App docs** | This product’s Change_Log, schema, runbooks | App repo only |

## Improve the kit, then let it flow down

Improve language-agnostic process in [LLM_Project_Template](https://github.com/AllenChildress/LLM_Project_Template), then merge it down into this repo. Improve shared Python behavior here, then merge it into each Python project. One PR per repo. Allen approves. Product docs stay in the product repo. See [docs/Template_Inheritance.md](docs/Template_Inheritance.md).

## License / sharing

Treat as your personal portable process unless you add a LICENSE. Redact any secrets before publishing.
