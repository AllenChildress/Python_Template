"""Tier markers are registered with the other kit markers."""

from __future__ import annotations

import pytest


def test_tier_markers_are_registered(pytestconfig: pytest.Config) -> None:
    """pytestconfig: this run's config. smoke, integration, and regression are kit tiers."""
    markers = pytestconfig.getini("markers")
    names = [str(line).split(":", 1)[0].strip() for line in markers]
    assert {"smoke", "integration", "regression"} <= set(names)
