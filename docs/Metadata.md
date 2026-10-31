# Metadata CSV

Non-user tuning lives in **one** checked-in CSV. It does not live in `.env`, and it does not live in a database.

`.env` stays for secrets and the few values a person really changes (a screen name, a token path, a database host). Connection settings for Postgres stay in `.env` as [Database.md](Database.md) shows. A retention count, a poll interval, or any other knob a person does not edit belongs here.

Allen’s design, 2026-10-31.

## Files

| File | Who writes it | In git? |
|------|----------------|---------|
| `metadata/settings.csv` | A coding agent, in a pull request. Set `updated` by hand to the date of that edit. | Yes |
| `metadata/local/settings.csv` | The app, through `write_measured`. `updated` becomes today. | No. `metadata/local/` is gitignored. |

Same columns in both files:

```text
category,variable,value,updated,description
```

The checked-in file shipped with Python_Template:

```text
category,variable,value,updated,description
app,log_retention_days,14,2026-10-31,How many days of log files to keep
ui,status_poll_seconds,5,2026-10-31,How often the status line refreshes
```

A product repo replaces those two rows with its own tuning. The header stays. See [Template_Inheritance.md](Template_Inheritance.md).

The app creates `metadata/local/` on the first measured write. The loader never writes `metadata/settings.csv`. Nothing in this design commits, pushes, or opens a pull request.

Do not put a secret in either CSV. Startup logs every loaded value.

## One loader

Every read and every sidecar write goes through the `src.metadata_settings` package. Import that package. The sibling modules are parts of the one loader, not a second door. Do not open the CSV with `csv` anywhere else.

```python
from pathlib import Path

from src.metadata_settings import EXACT_TOLERANCE, MetadataStore

root = Path(__file__).resolve().parents[1]
store = MetadataStore.from_root(root)
store.load()  # once, at startup
days = store.get_int("app", "log_retention_days", 14)
```

`root`: the checkout (or a temporary copy in a test). `from_root` joins `metadata/settings.csv` and `metadata/local/settings.csv`.

Lookup is **category + variable**. Each getter takes a required default:

| Getter | Accepts | Default is used when |
|--------|---------|----------------------|
| `get_int` | A whole signed integer (`14`, `-3`, `+2`) | The row is missing, or the cell is blank or not a whole integer (`1.5`, `soon`) |
| `get_float` | A finite number (`5`, `5.5`) | Missing, blank, or not a finite number (`inf`, `nan`, `soon`) |
| `get_str` | Any non-blank text | Missing or blank |
| `get_bool` | `1` `true` `yes` `on` / `0` `false` `no` `off` (any case) | Missing, blank, or any other token |

The cell is text. `get_int` and `get_bool` are two readings of that text. The caller picks the getter.

A missing **file** (`metadata/settings.csv` absent or with the wrong header) raises `MetadataError`. That is a broken checkout, not a missing key. A missing sidecar file means “no measured overrides” and is normal.

## Startup log

`load()` logs every loaded value at INFO, one line, including sidecar-only keys. The source is `checked-in default` or `sidecar override`. The date is the row’s `updated` column. Call `load()` once at startup. A getter calls `load()` if you have not, and that call still logs every value. A second `load()` reads again and logs again.

The sample file produces:

```text
metadata loaded category=app variable=log_retention_days value=14 source=checked-in default updated=2026-10-31
metadata loaded category=ui variable=status_poll_seconds value=5 source=checked-in default updated=2026-10-31
```

A sidecar row for the same category and variable replaces the checked-in row (value, updated, and description). The other rows stay checked-in defaults.

## Errors

A missing key or a bad cell is logged at ERROR. The getter returns the required default so the process can keep going. The sentence is the same one a status bar shows.

When the app has a status bar, pass an object with `show_error(message: str)`. This template has no window, so the argument is optional. `None` logs only.

```text
metadata: missing setting app.absent_days (int); using default 7
metadata: bad value for app.log_retention_days: 'soon' is not int; using default 14
```

The loader logs that sentence. It does not raise for a bad cell. A bad file still raises `MetadataError` after the same sentence is logged and, when a status bar was passed, shown.

## Measured values

```python
store.write_measured("app", "measured_span", "3", "samples taken today")
```

This updates or appends one sidecar row and sets `updated` to today (`YYYY-MM-DD`). Pass `description=None` (the default) to keep the description already in the sidecar. The checked-in file is not opened for writing.

The write logs:

```text
metadata sidecar wrote category=app variable=measured_span value=3 source=sidecar override updated=2026-10-31
```

Under pytest, or when `RUNNING_UNDER_TESTS=1`, `from_root` refuses the checkout root, and the loader refuses to read or write the checkout’s `metadata/local/` tree. Tests pass a temporary directory. A measured write with a blank category, variable, or value raises `MetadataError` and does not create the sidecar. `running_under_tests()` lives in `src/runtime_flags.py`. Soak tests use the same check (PROCESS § Executable production). The no-argument call reads the process environment. Tests of the check itself pass a mapping.

## Drift

A nightly log can ask which sidecar values are farther from the checked-in default than a tolerance. This repo does not schedule that log.

```python
for line in store.drift_lines(EXACT_TOLERANCE):
    logger.info("%s", line)
```

`tolerance` is an absolute numeric gap. The caller passes it. `EXACT_TOLERANCE` is `0.0` (any numeric difference counts).

| Sidecar vs default | Result |
|--------------------|--------|
| Same text | Not drift |
| Both finite numbers and the absolute gap is **greater than** tolerance | Drift |
| Gap equal to tolerance | Not drift |
| Both finite numbers that print differently and the gap is 0 (`14` and `14.0`) | Not drift |
| Text that is not numeric, and the text differs | Drift. Tolerance does not apply |
| Sidecar key with no checked-in row | Drift. The default is shown as `(none)` |

```text
metadata drift category=ui variable=banner default=hello sidecar=slow updated=2026-10-30
metadata drift category=app variable=measured_span default=(none) sidecar=3 updated=2026-10-30
```

`drifts_beyond(tolerance)` returns the same rows as objects (`SettingDrift`) for a caller that wants fields instead of lines.
