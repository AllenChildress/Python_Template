# Recommended libraries (Python staff kit)

Pick by product needs (see [Project.md](../Project.md) intake). This is a **starter menu**, not a mandate.

Install into a project virtual environment after Python is installed ([python.org/downloads](https://www.python.org/downloads/)):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -U pip
pip install pytest python-dotenv requests pydantic
# add drivers / UI stacks from the tables below as needed
```

Pin versions in `requirements.txt` or `pyproject.toml` for the app — recreate envs from that file.

## Core (most Python apps)

| Library | Why |
|---------|-----|
| **Python 3.11+** (3.12 preferred) | Modern typing, performance |
| **pytest** | Unit, smoke, integration, regression |
| **python-dotenv** | Local `.env` without committing secrets |
| **requests** or **httpx** | HTTP APIs (httpx if async later) |
| **pydantic** (optional) | Validated config / API models |

## Desktop UI (if intake = desktop)

| Library | Why |
|---------|-----|
| **PyQt6** or **PySide6** | Mature desktop UI |
| **Qt WebEngine** (optional) | Embedded HTML / charts |

## Web UI (if intake = web)

| Library | Why |
|---------|-----|
| **FastAPI** or **Flask** | API / light web |
| **SQLAlchemy** or raw SQL | DB access layer |

## Data / analytics (if needed)

| Library | Why |
|---------|-----|
| **pandas** | Tables, time series, joins |
| **numpy** | Numeric arrays |

## Database drivers

| Choice | Driver / notes |
|--------|----------------|
| **PostgreSQL** | `psycopg` (v3) — general default for multi-user apps |
| **SQLite** | stdlib `sqlite3` — single-user, local, simple |
| **TimescaleDB** | Postgres extension — time-series / metrics / events (see [Database.md](Database.md)) |

## Do not commit

Lockfiles (`requirements.txt` / `pyproject.toml`) yes; `.env` and secrets no.

Wire libraries in the app’s own dependency file after intake — this kit only documents the menu.
