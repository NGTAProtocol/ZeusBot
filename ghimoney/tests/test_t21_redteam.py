"""T-21: red-team additions not already covered by T-19/T-20's own test
suites. Everything else in the T-21 checklist (fake stars/forks, missing
data never zero, Adoption+Dependency missing, coverage <60%,
renormalization, determinism, Go/404 never zero) is already exercised by
test_redteam.py, test_scoring.py, test_determinism.py,
test_depsdev_dependents_evidence.py and test_t20_full_impact_score.py; this
file adds only what those do not cover:

1. dependents_total_count must influence only the "dependency" dimension;
2. T-19's outgoing-dependency evidence ("dependencies" key) must never be
   read as dependents, even if both happen to be present in one snapshot;
3. anchor=1000 sensitivity across representative and edge values, checked
   for monotonicity and boundedness -- a documented finding, not a fix.
"""

from __future__ import annotations

import math

import pytest

from conftest import make_snapshot
from conftest_depsdev import make_dependents_snapshot, make_depsdev_snapshot
from ghimoney.depsdev_dependents_evidence import build_dependents_evidence
from ghimoney.engine import analyze
from ghimoney.models import Availability
from ghimoney.normalization import normalize


# --- 1. dependents_total_count scopes only to "dependency" -----------------

def test_dependents_value_changes_only_the_dependency_dimension(methodology):
    low = build_dependents_evidence(
        make_dependents_snapshot("npm", "pkg", "1.0.0", dependents="t20a_cargo_serde_dependents"),
        "npm", "pkg", "1.0.0", methodology)
    high = build_dependents_evidence(
        make_dependents_snapshot("npm", "pkg", "1.0.0", dependents="t20a_npm_lodash_dependents"),
        "npm", "pkg", "1.0.0", methodology)

    report_low = analyze(make_snapshot(), methodology, extra_evidence=low)
    report_high = analyze(make_snapshot(), methodology, extra_evidence=high)

    dims_low = {d["dimension"]: d for d in report_low["dimensions"]}
    dims_high = {d["dimension"]: d for d in report_high["dimensions"]}
    assert dims_low["dependency"]["score"] != dims_high["dependency"]["score"]
    for dim in ("adoption", "maintenance", "quality", "security", "community"):
        assert dims_low[dim] == dims_high[dim], f"{dim} must not be affected by dependents"
    # Confidence/Risk are also dimension-agnostic aggregates that must not
    # shift just because the dependents value differs.
    assert report_low["risk"] == report_high["risk"]


# --- 2. T-19's GetDependencies key must never be read as dependents --------

def test_dependencies_key_is_never_used_as_dependents(methodology):
    # A snapshot shaped like T-19's (a "dependencies" key with a real,
    # populated outgoing-dependency graph) but with NO "dependents" key at
    # all: if build_dependents_evidence ever accidentally fell back to
    # reading "dependencies", this would wrongly become VERIFIED.
    snap = make_depsdev_snapshot("npm", "express", "4.19.2",
                                 package="t1_npm_lodash_package",
                                 dependencies="t4_npm_express_dependencies")
    record = build_dependents_evidence(snap, "npm", "express", "4.19.2", methodology)[0]
    assert record.availability is Availability.NOT_AVAILABLE
    assert record.raw_value is None


def test_dependencies_key_ignored_even_when_dependents_also_present(methodology):
    # Both keys present in the same snapshot (not a real ingestion shape,
    # but a deliberately adversarial one): the evidence must come only from
    # "dependents", and its value must not equal the outgoing-graph counts.
    from ghimoney.snapshot import Snapshot
    dependents_snap = make_dependents_snapshot("npm", "express", "4.19.2",
                                                dependents="t20a_npm_lodash_dependents")
    depsdev_snap = make_depsdev_snapshot("npm", "express", "4.19.2",
                                         dependencies="t4_npm_express_dependencies")
    mixed = Snapshot(target="npm:express@4.19.2", source="deps-dev-api-v3alpha-dependents",
                     as_of=dependents_snap.as_of, api_version="v3alpha",
                     responses={**depsdev_snap.responses, **dependents_snap.responses})
    record = build_dependents_evidence(mixed, "npm", "express", "4.19.2", methodology)[0]
    assert record.raw_value == 22623  # from "dependents", not the 31/37 in "dependencies"


# --- 3. anchor=1000 sensitivity (finding, not a fix) ------------------------

REPRESENTATIVE_DEPENDENT_COUNTS = [0, 1, 68, 500, 1000, 3041, 9397, 22623, 100_000]


def test_anchor_curve_is_monotonic_and_bounded(methodology):
    cfg = methodology.metrics["dependents_total_count"]
    scores = [normalize(x, cfg) for x in REPRESENTATIVE_DEPENDENT_COUNTS]
    assert all(0.0 <= s <= 100.0 for s in scores)
    assert scores == sorted(scores)  # monotonic non-decreasing


def test_anchor_saturates_far_below_observed_real_values(methodology):
    """FINDING (documented in docs/T21_TEST_REPORT.md, not fixed here per
    instructions): anchor=1000 makes every T-20A real package at or above
    ~1000 dependents score exactly 100, losing all discrimination between
    e.g. requests (3,041), guava (9,397) and lodash (22,623)."""
    cfg = methodology.metrics["dependents_total_count"]
    real_counts = {"serde": 68, "requests": 3041, "guava": 9397, "lodash": 22623}
    scores = {name: normalize(x, cfg) for name, x in real_counts.items()}
    assert scores["serde"] < 100.0  # still discriminated (below anchor)
    assert scores["requests"] == scores["guava"] == scores["lodash"] == 100.0
    # Half of the anchor's saturation curve is reached well before 500:
    # discrimination is compressed into a narrow low range.
    assert normalize(500, cfg) == pytest.approx(100 * math.log1p(500) / math.log1p(1000), rel=1e-9)
