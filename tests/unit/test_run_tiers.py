"""Fail-fast tier chain. Exit 5 (no tests collected) counts as a pass."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_tiers import main, tier_stops_chain  # noqa: E402  chain rule under test


@pytest.mark.parametrize(
    ("exit_code", "stops"),
    [(0, False), (5, False), (1, True), (2, True), (3, True), (4, True)],
)
def test_only_pass_and_empty_collection_continue(exit_code: int, stops: bool) -> None:
    """exit_code: a pytest return code. stops: whether the next tier must not start."""
    assert tier_stops_chain(exit_code) is stops


def test_empty_tier_does_not_stop_the_chain() -> None:
    """tiers: unit passes, smoke collects nothing, integration passes.

    python: stand-in interpreter. The fake runner does not launch it.
    runner: returns the canned code for each tier path.
    """
    seen: list[str] = []
    codes = {"tests/unit": 0, "tests/smoke": 5, "tests/integration": 0}

    def runner(python: str, tier: str) -> int:
        """python: ignored stand-in. tier: the path main asked to run."""
        del python
        seen.append(tier)
        return codes[tier]

    result = main(
        ["tests/unit", "tests/smoke", "tests/integration"],
        "python",
        runner,
    )
    assert result == 0
    assert seen == ["tests/unit", "tests/smoke", "tests/integration"]


def test_failed_tier_stops_and_names_the_tier(capsys: pytest.CaptureFixture[str]) -> None:
    """tiers: unit passes, smoke fails, integration must not run.

    python: stand-in interpreter. capsys: captures the stop line.
    runner: returns the canned code for each tier path.
    """
    seen: list[str] = []
    codes = {"tests/unit": 0, "tests/smoke": 1, "tests/integration": 0}

    def runner(python: str, tier: str) -> int:
        """python: ignored stand-in. tier: the path main asked to run."""
        del python
        seen.append(tier)
        return codes[tier]

    result = main(
        ["tests/unit", "tests/smoke", "tests/integration"],
        "python",
        runner,
    )
    assert result == 1
    assert seen == ["tests/unit", "tests/smoke"]
    assert "stopped at tests/smoke (exit 1)" in capsys.readouterr().err


def test_no_tiers_is_a_usage_error() -> None:
    """tiers: empty. python: unused. The runner must not be called."""
    called = False

    def runner(python: str, tier: str) -> int:
        """python: unused. tier: unused. A call here fails the test."""
        del python, tier
        nonlocal called
        called = True
        return 0

    assert main([], "python", runner) == 2
    assert called is False
