"""Metadata CSV load, override order, bad values, startup lines, and sidecar writes.

Files live under tmp_path. The checkout sidecar is only named, never written.
"""

from __future__ import annotations

import logging  # capture startup lines and error sentences
from collections.abc import Callable  # optional clock passed into the store
from datetime import date  # injected sidecar clock
from pathlib import Path  # temporary CSV paths

import pytest  # raises, parametrize, caplog, and tmp_path

from src.metadata_settings import (  # the one loader every caller uses
    COLUMNS,
    EXACT_TOLERANCE,
    LOGGER_NAME,
    SOURCE_DEFAULT,
    SOURCE_SIDECAR,
    MetadataError,
    MetadataStore,
    SettingDrift,
    StatusBar,
    checkout_root,
    defaults_path,
    sidecar_path,
)

HEADER = ",".join(COLUMNS) + "\n"
APP_ROW = "app,log_retention_days,14,2026-10-31,How many days of log files to keep\n"
UI_ROW = "ui,status_poll_seconds,5,2026-10-31,How often the status line refreshes\n"
SAMPLE_CLOCK = date(2026, 10, 31)
APP_LOADED = (
    "metadata loaded category=app variable=log_retention_days "
    "value=14 source=checked-in default updated=2026-10-31"
)
UI_LOADED = (
    "metadata loaded category=ui variable=status_poll_seconds "
    "value=5 source=checked-in default updated=2026-10-31"
)


class _Bar:
    """Collects status-bar sentences so a test can read them back."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def show_error(self, message: str) -> None:
        """message: the sentence the loader also writes to the log."""
        self.errors.append(message)


def _clock() -> date:
    """Fixed day so sidecar writes do not read the wall clock."""
    return SAMPLE_CLOCK


def _write_csv(path: Path, body: str) -> Path:
    """path: destination file. body: full CSV text, including the header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _store(
    tmp_path: Path,
    rows: str,
    sidecar_rows: str | None = None,
    status: StatusBar | None = None,
    today: Callable[[], date] | None = None,
) -> MetadataStore:
    """Build a store whose files live under tmp_path.

    tmp_path: the test's temporary directory.
    rows: CSV data lines for the checked-in file, after the header.
    sidecar_rows: CSV data lines for the sidecar. None means no sidecar file.
    status: status bar double. None logs only.
    today: clock for measured writes. None uses the fixed sample day.
    """
    checked_in = _write_csv(defaults_path(tmp_path), HEADER + rows)
    sidecar = sidecar_path(tmp_path)
    if sidecar_rows is not None:
        _write_csv(sidecar, HEADER + sidecar_rows)
    return MetadataStore(
        checked_in,
        sidecar,
        status=status,
        today=_clock if today is None else today,
    )


def _loaded_messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    """caplog: captured log. Returns startup lines in emit order."""
    return [
        record.getMessage()
        for record in caplog.records
        if record.getMessage().startswith("metadata loaded ")
    ]


def test_startup_log_names_every_value_source_and_date(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """rows: the two sample settings. caplog: INFO on the metadata logger."""
    store = _store(tmp_path, APP_ROW + UI_ROW)
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        store.load()
    assert _loaded_messages(caplog) == [APP_LOADED, UI_LOADED]
    assert SOURCE_DEFAULT in APP_LOADED


def test_sidecar_override_wins_and_keeps_the_other_default(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """sidecar_rows: a newer app value. The ui row stays the checked-in default."""
    sidecar = "app,log_retention_days,21,2026-10-30,measured\n"
    store = _store(tmp_path, APP_ROW + UI_ROW, sidecar_rows=sidecar)
    before = defaults_path(tmp_path).read_bytes()
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        store.load()
    assert store.get_int("app", "log_retention_days", 0) == 21
    assert store.get_float("ui", "status_poll_seconds", 0.0) == 5.0
    assert defaults_path(tmp_path).read_bytes() == before
    loaded = _loaded_messages(caplog)
    assert loaded[0] == (
        "metadata loaded category=app variable=log_retention_days "
        f"value=21 source={SOURCE_SIDECAR} updated=2026-10-30"
    )
    assert loaded[1] == UI_LOADED


def test_missing_sidecar_loads_the_defaults(tmp_path: Path) -> None:
    """sidecar_rows is omitted, so no sidecar file exists."""
    store = _store(tmp_path, APP_ROW)
    store.load()
    assert store.get_int("app", "log_retention_days", 0) == 14
    assert store.drifts_beyond(EXACT_TOLERANCE) == ()


def test_missing_key_returns_the_default_and_reports(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """default: 7. The category and variable are absent from both files."""
    bar = _Bar()
    store = _store(tmp_path, APP_ROW, status=bar)
    store.load()
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        found = store.get_int("app", "absent_days", 7)
    message = "metadata: missing setting app.absent_days (int); using default 7"
    assert found == 7
    assert message in caplog.text
    assert bar.errors == [message]


def test_bad_int_returns_the_default_and_reports(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """rows: a non-integer cell. default: 14, the required fallback."""
    bar = _Bar()
    store = _store(tmp_path, "app,log_retention_days,soon,2026-10-31,days\n", status=bar)
    store.load()
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        found = store.get_int("app", "log_retention_days", 14)
    message = (
        "metadata: bad value for app.log_retention_days: 'soon' is not int; using default 14"
    )
    assert found == 14
    assert message in caplog.text
    assert bar.errors == [message]


def test_bad_float_returns_the_default(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """rows: a non-numeric cell. default: 5.0."""
    store = _store(tmp_path, "ui,status_poll_seconds,soon,2026-10-31,seconds\n")
    store.load()
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        found = store.get_float("ui", "status_poll_seconds", 5.0)
    assert found == 5.0
    assert "is not float; using default 5.0" in caplog.text


def test_blank_str_returns_the_default(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """rows: a blank value cell. default: the fallback label."""
    store = _store(tmp_path, "ui,banner,,2026-10-31,label\n")
    store.load()
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        found = store.get_str("ui", "banner", "plain")
    assert found == "plain"
    assert "is not str; using default 'plain'" in caplog.text


def test_good_values_ignore_the_fallback(tmp_path: Path) -> None:
    """rows: an integer, a float, and a string. Each default is a different sentinel."""
    rows = (
        "app,log_retention_days,14,2026-10-31,days\n"
        "ui,status_poll_seconds,5.5,2026-10-31,seconds\n"
        "ui,banner,hello,2026-10-31,label\n"
    )
    store = _store(tmp_path, rows)
    store.load()
    assert store.get_int("app", "log_retention_days", 0) == 14
    assert store.get_float("ui", "status_poll_seconds", 0.0) == 5.5
    assert store.get_str("ui", "banner", "other") == "hello"


def test_negative_integer(tmp_path: Path) -> None:
    """rows: a signed integer. default: 0, which must not replace a real value."""
    store = _store(tmp_path, "app,offset,-3,2026-10-31,signed\n")
    store.load()
    assert store.get_int("app", "offset", 0) == -3


@pytest.mark.parametrize("token", ["true", "YES", "1", "on"])
def test_true_tokens(tmp_path: Path, token: str) -> None:
    """token: a cell that must read as True. default False proves the cell won."""
    store = _store(tmp_path, f"ui,enabled,{token},2026-10-31,flag\n")
    store.load()
    assert store.get_bool("ui", "enabled", False) is True


@pytest.mark.parametrize("token", ["false", "no", "0", "OFF"])
def test_false_tokens(tmp_path: Path, token: str) -> None:
    """token: a cell that must read as False. default True proves the cell won."""
    store = _store(tmp_path, f"ui,enabled,{token},2026-10-31,flag\n")
    store.load()
    assert store.get_bool("ui", "enabled", True) is False


def test_bad_bool_returns_the_default(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """rows: a token outside the bool sets. default: False."""
    store = _store(tmp_path, "ui,enabled,maybe,2026-10-31,flag\n")
    store.load()
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        found = store.get_bool("ui", "enabled", False)
    assert found is False
    assert "is not bool; using default False" in caplog.text


def test_write_measured_sets_today_and_leaves_defaults(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """today: 2026-10-31 from the store clock. description is kept when omitted later."""
    store = _store(tmp_path, APP_ROW + UI_ROW)
    before = defaults_path(tmp_path).read_bytes()
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        store.load()
        store.write_measured("app", "log_retention_days", "21", "measured span")
    sidecar = sidecar_path(tmp_path).read_text(encoding="utf-8")
    assert "app,log_retention_days,21,2026-10-31,measured span" in sidecar
    assert defaults_path(tmp_path).read_bytes() == before
    assert store.get_int("app", "log_retention_days", 0) == 21
    assert (
        "metadata sidecar wrote category=app variable=log_retention_days "
        "value=21 source=sidecar override updated=2026-10-31"
    ) in caplog.text
    store.write_measured("app", "log_retention_days", "22")
    kept = sidecar_path(tmp_path).read_text(encoding="utf-8")
    assert "app,log_retention_days,22,2026-10-31,measured span" in kept
    store.write_measured("app", "log_retention_days", "23", "replaced")
    replaced = sidecar_path(tmp_path).read_text(encoding="utf-8")
    assert "app,log_retention_days,23,2026-10-31,replaced" in replaced
    assert "status_poll_seconds" not in replaced


def test_write_measured_appends_and_quotes_commas(tmp_path: Path) -> None:
    """description contains a comma, so the CSV writer must quote it."""
    store = _store(tmp_path, APP_ROW)
    store.load()
    store.write_measured("app", "measured_span", "3", "one, two")
    reloaded = MetadataStore(
        defaults_path(tmp_path),
        sidecar_path(tmp_path),
        today=_clock,
    )
    reloaded.load()
    assert reloaded.get_int("app", "measured_span", 0) == 3
    text = sidecar_path(tmp_path).read_text(encoding="utf-8")
    assert "one, two" in text


def test_blank_measured_value_does_not_create_a_sidecar(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """value: whitespace. The sidecar file must stay absent."""
    store = _store(tmp_path, APP_ROW)
    store.load()
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        with pytest.raises(MetadataError, match="measured value"):
            store.write_measured("app", "log_retention_days", "  ")
    assert not sidecar_path(tmp_path).is_file()
    assert "measured value" in caplog.text


def test_drift_lists_numeric_text_and_sidecar_only_rows(tmp_path: Path) -> None:
    """sidecar: a gap equal to 0.5, an equal string, a far number, and a new key.

    tolerance 0.5 keeps the equal gap and the equal text.
    """
    rows = (
        "app,log_retention_days,14,2026-10-31,days\n"
        "ui,banner,hello,2026-10-31,label\n"
        "ui,status_poll_seconds,5,2026-10-31,seconds\n"
    )
    sidecar = (
        "app,log_retention_days,14.5,2026-10-30,close\n"
        "ui,banner,hello,2026-10-30,same\n"
        "ui,status_poll_seconds,9,2026-10-30,far\n"
        "app,measured_span,3,2026-10-30,new\n"
    )
    store = _store(tmp_path, rows, sidecar_rows=sidecar)
    store.load()
    assert store.drifts_beyond(0.5) == (
        SettingDrift("app", "measured_span", None, "3", "2026-10-30"),
        SettingDrift("ui", "status_poll_seconds", "5", "9", "2026-10-30"),
    )
    assert store.drifts_beyond(EXACT_TOLERANCE) == (
        SettingDrift("app", "log_retention_days", "14", "14.5", "2026-10-30"),
        SettingDrift("app", "measured_span", None, "3", "2026-10-30"),
        SettingDrift("ui", "status_poll_seconds", "5", "9", "2026-10-30"),
    )


def test_equal_numeric_text_is_not_drift(tmp_path: Path) -> None:
    """sidecar value 14.0 matches default 14. tolerance is zero."""
    sidecar = "app,log_retention_days,14.0,2026-10-30,same number\n"
    store = _store(tmp_path, APP_ROW, sidecar_rows=sidecar)
    store.load()
    assert store.drifts_beyond(EXACT_TOLERANCE) == ()


def test_text_change_drifts_at_any_tolerance(tmp_path: Path) -> None:
    """sidecar text differs, and neither side is a number. tolerance is large."""
    rows = "ui,banner,hello,2026-10-31,label\n"
    sidecar = "ui,banner,slow,2026-10-30,changed\n"
    store = _store(tmp_path, rows, sidecar_rows=sidecar)
    store.load()
    assert store.drift_lines(100.0) == (
        "metadata drift category=ui variable=banner default=hello sidecar=slow updated=2026-10-30",
    )


def test_gap_equal_to_tolerance_is_not_drift(tmp_path: Path) -> None:
    """gap is 0.5 and tolerance is 0.5. Drift is only a gap greater than tolerance."""
    sidecar = "app,log_retention_days,14.5,2026-10-30,edge\n"
    store = _store(tmp_path, APP_ROW, sidecar_rows=sidecar)
    store.load()
    assert store.drifts_beyond(0.5) == ()


def test_negative_tolerance_is_an_error(tmp_path: Path) -> None:
    """tolerance: -1. The call names the bad tolerance."""
    store = _store(tmp_path, APP_ROW)
    store.load()
    with pytest.raises(MetadataError, match="tolerance"):
        store.drifts_beyond(-1)


def test_bad_header_is_logged(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """body: a header that is not the five-column contract."""
    path = _write_csv(defaults_path(tmp_path), "name,value\n")
    store = MetadataStore(path, sidecar_path(tmp_path), today=_clock)
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        with pytest.raises(MetadataError, match="header"):
            store.load()
    assert "header" in caplog.text


def test_duplicate_key_is_an_error(tmp_path: Path) -> None:
    """rows: the same category and variable twice."""
    store = _store(tmp_path, APP_ROW + APP_ROW)
    with pytest.raises(MetadataError, match="repeats app.log_retention_days"):
        store.load()


def test_missing_defaults_file_is_logged_and_shown(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """defaults_path: a file that was never written. status: collects the sentence."""
    bar = _Bar()
    store = MetadataStore(
        defaults_path(tmp_path),
        sidecar_path(tmp_path),
        status=bar,
        today=_clock,
    )
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        with pytest.raises(MetadataError, match="missing"):
            store.load()
    assert bar.errors
    assert bar.errors[0] in caplog.text


def test_row_missing_updated_is_an_error(tmp_path: Path) -> None:
    """rows: the updated cell is empty."""
    store = _store(tmp_path, "app,log_retention_days,14,,days\n")
    with pytest.raises(MetadataError, match="missing category, variable, or updated"):
        store.load()


def test_bom_header_still_loads(tmp_path: Path) -> None:
    """body: the sample CSV with a UTF-8 BOM in front of the header."""
    payload = (HEADER + APP_ROW).encode("utf-8")
    path = defaults_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"\xef\xbb\xbf" + payload)
    store = MetadataStore(path, sidecar_path(tmp_path), today=_clock)
    store.load()
    assert store.get_int("app", "log_retention_days", 0) == 14


def test_header_only_sidecar_adds_no_overrides(tmp_path: Path) -> None:
    """sidecar_rows: empty string, so the file is the header and nothing else."""
    store = _store(tmp_path, APP_ROW, sidecar_rows="")
    store.load()
    assert store.get_int("app", "log_retention_days", 0) == 14


def test_checkout_sidecar_is_not_read_or_written_under_tests(tmp_path: Path) -> None:
    """sidecar: the checkout metadata/local file. running_under_tests is true here."""
    sidecar = sidecar_path(checkout_root())
    before = sidecar.read_bytes() if sidecar.is_file() else None
    store = MetadataStore(defaults_path(tmp_path), sidecar, today=_clock)
    _write_csv(defaults_path(tmp_path), HEADER + APP_ROW)
    with pytest.raises(MetadataError, match="running_under_tests"):
        store.load()
    after = sidecar.read_bytes() if sidecar.is_file() else None
    assert after == before


def test_from_root_refuses_the_checkout_during_tests() -> None:
    """root: this checkout. The guard refuses it while pytest is running."""
    with pytest.raises(MetadataError, match="running_under_tests"):
        MetadataStore.from_root(checkout_root())


def test_outside_a_test_run_the_guard_stays_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """monkeypatch: running_under_tests returns false, so a temporary sidecar write proceeds.

    The patched function is the binding metadata_settings calls.
    """
    monkeypatch.setattr("src.metadata_settings.running_under_tests", lambda: False)
    store = _store(tmp_path, APP_ROW)
    store.load()
    store.write_measured("app", "log_retention_days", "21", "measured")
    assert sidecar_path(tmp_path).is_file()


def test_from_root_reads_a_temporary_layout(tmp_path: Path) -> None:
    """root: tmp_path, which has metadata/settings.csv and no sidecar."""
    _write_csv(defaults_path(tmp_path), HEADER + APP_ROW)
    store = MetadataStore.from_root(tmp_path, today=_clock)
    store.load()
    assert store.get_int("app", "log_retention_days", 0) == 14


def test_shipped_header_matches_the_loader_contract() -> None:
    """The checked-in sample uses the column tuple, in that order."""
    text = defaults_path(checkout_root()).read_text(encoding="utf-8-sig")
    assert text.splitlines()[0] == ",".join(COLUMNS)


def test_python_template_sample_rows(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """The shipped sample is the pair documented in docs/Metadata.md.

    tmp_path: holds the sidecar so the checkout sidecar is not read.
    """
    store = MetadataStore(defaults_path(checkout_root()), sidecar_path(tmp_path), today=_clock)
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        store.load()
    assert store.get_int("app", "log_retention_days", 0) == 14
    assert store.get_float("ui", "status_poll_seconds", 0.0) == 5.0
    assert _loaded_messages(caplog) == [APP_LOADED, UI_LOADED]


def test_sidecar_only_row_is_in_the_startup_log(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """sidecar_rows: a key the checked-in file does not have."""
    store = _store(tmp_path, APP_ROW, sidecar_rows="app,measured_span,3,2026-10-30,new\n")
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        store.load()
    assert (
        "metadata loaded category=app variable=measured_span "
        "value=3 source=sidecar override updated=2026-10-30"
    ) in caplog.text
