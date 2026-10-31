# template-owned: Python_Template
"""Whether this process is a test run.

Soak tests and the metadata loader share this check. See docs/PROCESS.md
(Executable production) and docs/Metadata.md.
"""

from __future__ import annotations  # postponed annotations on the public signature

import os  # PYTEST_CURRENT_TEST and RUNNING_UNDER_TESTS from the process environment
from collections.abc import Mapping  # environ argument without requiring a dict

# Pytest sets this for the test that is running. Blank means unset.
PYTEST_CURRENT_TEST_ENV = "PYTEST_CURRENT_TEST"
# Explicit flag for soak tests and other harnesses that are not pytest.
RUNNING_UNDER_TESTS_ENV = "RUNNING_UNDER_TESTS"
RUNNING_UNDER_TESTS_VALUE = "1"


def running_under_tests(environ: Mapping[str, str] | None = None) -> bool:
    """True when pytest is on the current test, or RUNNING_UNDER_TESTS is 1.

    environ: environment to read. None reads the process environment.
    PYTEST_CURRENT_TEST is set by pytest for the current test.
    RUNNING_UNDER_TESTS is the explicit flag for soak and other harnesses.
    """
    env = os.environ if environ is None else environ
    if env.get(PYTEST_CURRENT_TEST_ENV, "").strip() != "":
        return True
    return env.get(RUNNING_UNDER_TESTS_ENV, "").strip() == RUNNING_UNDER_TESTS_VALUE
