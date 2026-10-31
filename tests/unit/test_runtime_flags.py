"""running_under_tests reads an environment map. No files, no clock."""

from __future__ import annotations

from src.runtime_flags import (  # the shared test-run check
    PYTEST_CURRENT_TEST_ENV,
    RUNNING_UNDER_TESTS_ENV,
    RUNNING_UNDER_TESTS_VALUE,
    running_under_tests,
)


def test_empty_environment_is_not_a_test_run() -> None:
    """environ: no pytest variable and no explicit flag."""
    assert running_under_tests({}) is False


def test_pytest_current_test_counts() -> None:
    """environ PYTEST_CURRENT_TEST: the node id pytest sets for the current test."""
    environ = {PYTEST_CURRENT_TEST_ENV: "tests/unit/test_runtime_flags.py::test_example"}
    assert running_under_tests(environ) is True


def test_blank_pytest_variable_does_not_count() -> None:
    """environ PYTEST_CURRENT_TEST is whitespace, which is the same as unset."""
    assert running_under_tests({PYTEST_CURRENT_TEST_ENV: "  "}) is False


def test_explicit_flag_counts() -> None:
    """environ RUNNING_UNDER_TESTS: the soak-harness flag, set to 1."""
    assert running_under_tests({RUNNING_UNDER_TESTS_ENV: RUNNING_UNDER_TESTS_VALUE}) is True


def test_other_flag_values_do_not_count() -> None:
    """environ RUNNING_UNDER_TESTS is set, but not to the accepted value."""
    assert running_under_tests({RUNNING_UNDER_TESTS_ENV: "yes"}) is False


def test_no_argument_sees_the_pytest_process() -> None:
    """environ is omitted, so the function reads the process environment.

    Pytest sets PYTEST_CURRENT_TEST for this test.
    """
    assert running_under_tests() is True
