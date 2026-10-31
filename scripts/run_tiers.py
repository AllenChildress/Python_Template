"""Run pytest tiers in order. Exit 5 (no tests collected) counts as a pass.

Any other nonzero pytest code stops the chain. The script exits with that
code and names the tier.

Usage (repo root, project interpreter):

    python scripts/run_tiers.py tests/unit tests/smoke tests/integration tests/regression
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable

# pytest exits 5 when the target exists and collects nothing.
NO_TESTS_COLLECTED = 5
USAGE_EXIT = 2

# python: interpreter that launches pytest. tier: one pytest target path.
Runner = Callable[[str, str], int]


def tier_stops_chain(exit_code: int) -> bool:
    """Return whether this pytest code stops the next tier.

    exit_code: the return code from one pytest process.
    0 passed. 5 collected nothing. Both let the chain continue.
    """
    return exit_code not in (0, NO_TESTS_COLLECTED)


def run_pytest(python: str, tier: str) -> int:
    """Run pytest on one tier and return its exit code.

    python: the project interpreter that should launch pytest.
    tier: a pytest target path. The caller supplies it. This function does not pick a path.
    """
    completed = subprocess.run(
        [python, "-m", "pytest", tier, "-q"],
        check=False,
    )
    return int(completed.returncode)


def main(tiers: list[str], python: str, runner: Runner = run_pytest) -> int:
    """Run each tier in order. Stop on the first real failure.

    tiers: pytest targets in run order. An empty list is a usage error.
    python: interpreter passed through to the runner.
    runner: maps (python, tier) to an exit code. Tests pass a fake. Default runs pytest.
    """
    if not tiers:
        print(
            "usage: python scripts/run_tiers.py <tier> [<tier> ...]",
            file=sys.stderr,
        )
        return USAGE_EXIT
    for tier in tiers:
        code = runner(python, tier)
        if tier_stops_chain(code):
            print(f"stopped at {tier} (exit {code})", file=sys.stderr)
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], sys.executable))
