"""Dependents evidence for the "dependency" dimension, from real T-20A
fixtures (T-20, D-12). No network."""

from __future__ import annotations

import math

from conftest_depsdev import make_dependents_snapshot
from ghimoney.depsdev_dependents_evidence import METRIC_NAME, build_dependents_evidence
from ghimoney.models import Availability


def _record(methodology, ecosystem, name, version, **keyed_fixtures):
    snap = make_dependents_snapshot(ecosystem, name, version, **keyed_fixtures)
    return build_dependents_evidence(snap, ecosystem, name, version, methodology)[0]


# --- verified dependents, all four supported ecosystems --------------------

def test_npm_verified_dependents_are_scored(methodology):
    r = _record(methodology, "npm", "lodash", "4.17.21",
               dependents="t20a_npm_lodash_dependents")
    assert r.availability is Availability.VERIFIED
    assert r.raw_value == 22623
    assert r.evidence_kind == "lower_bound"
    cfg = methodology.metrics[METRIC_NAME]
    expected = 100 * min(1.0, math.log1p(22623) / math.log1p(cfg.anchor))
    assert r.normalized_value == expected
    assert r.normalized_value == 100.0  # saturated well above the anchor


def test_pypi_verified_dependents(methodology):
    r = _record(methodology, "pypi", "requests", "2.31.0",
               dependents="t20a_pypi_requests_dependents")
    assert r.availability is Availability.VERIFIED
    assert r.raw_value == 3041


def test_maven_verified_dependents(methodology):
    r = _record(methodology, "maven", "com.google.guava:guava", "32.1.3-jre",
               dependents="t20a_maven_guava_dependents")
    assert r.availability is Availability.VERIFIED
    assert r.raw_value == 9397


def test_cargo_verified_dependents_below_anchor(methodology):
    r = _record(methodology, "cargo", "serde", "1.0.203",
               dependents="t20a_cargo_serde_dependents")
    assert r.availability is Availability.VERIFIED
    assert r.raw_value == 68
    cfg = methodology.metrics[METRIC_NAME]
    assert 0 < r.normalized_value < 100  # not saturated, below the anchor


# --- Go: never available, never zero (D-12 condition) ----------------------

def test_go_dependents_is_not_available_never_zero(methodology):
    r = _record(methodology, "go", "github.com/pkg/errors", "v0.9.1")  # no fixture at all
    assert r.availability is Availability.NOT_AVAILABLE
    assert r.raw_value is None
    assert r.normalized_value is None
    assert "not evidence of zero dependents" in r.note


def test_go_ignores_a_dependents_key_even_if_present(methodology):
    # Defensive: the ecosystem gate applies first, regardless of what a
    # snapshot happens to contain (mirrors T-19's same defensive test).
    r = _record(methodology, "go", "github.com/pkg/errors", "v0.9.1",
               dependents="t20a_go_pkgerrors_dependents_404")
    assert r.availability is Availability.NOT_AVAILABLE
    assert "source-level limitation" in r.note


# --- UNKNOWN / missing data --------------------------------------------------

def test_missing_dependents_request_is_not_available(methodology):
    from ghimoney.snapshot import Snapshot
    snap = Snapshot(target="npm:x@1.0.0", source="deps-dev-api-v3alpha-dependents",
                    as_of="2026-09-23T12:00:00Z", api_version="v3alpha", responses={})
    from ghimoney.depsdev_dependents_evidence import build_dependents_evidence
    r = build_dependents_evidence(snap, "npm", "x", "1.0.0", methodology)[0]
    assert r.availability is Availability.NOT_AVAILABLE
    assert r.raw_value is None


# --- 404 / errors: never zero (D-03/D-12 discipline) ------------------------

def test_404_on_supported_ecosystem_is_ambiguous_never_zero(methodology):
    # T-20A: the same "dependents not found" 404 is returned for a package
    # that genuinely does not exist -- must never be read as zero.
    r = _record(methodology, "npm", "this-package-does-not-exist-ghimoney-test-12345", "1.0.0",
               dependents="t20a_npm_nonexistent_dependents_404")
    assert r.availability is Availability.NOT_AVAILABLE
    assert r.raw_value is None
    assert "never interpreted as zero" in r.note


def test_transport_error_is_not_available(methodology):
    from ghimoney.snapshot import Response, Snapshot
    snap = Snapshot(target="npm:x@1.0.0", source="deps-dev-api-v3alpha-dependents",
                    as_of="2026-09-23T12:00:00Z", api_version="v3alpha",
                    responses={"dependents": Response(endpoint="fixture", status=503, body="")})
    r = build_dependents_evidence(snap, "npm", "x", "1.0.0", methodology)[0]
    assert r.availability is Availability.NOT_AVAILABLE
    assert "transport_error" in r.note


# --- source clearly marked experimental -------------------------------------

def test_method_marks_source_as_experimental(methodology):
    r = _record(methodology, "npm", "lodash", "4.17.21",
               dependents="t20a_npm_lodash_dependents")
    assert "EXPERIMENTAL SOURCE" in r.method
    assert "v3alpha" in r.method


def test_uses_real_methodology_version_not_an_independent_tag(methodology):
    # Unlike T-19's outgoing evidence (always tagged with an independent,
    # unscored version), this evidence is scored under the real, current
    # methodology version.
    r = _record(methodology, "npm", "lodash", "4.17.21",
               dependents="t20a_npm_lodash_dependents")
    assert r.methodology_version == methodology.methodology_version
    assert r.methodology_version != "GHIM-DEPENDENCY-EVIDENCE-0.1"


def test_confidence_reuses_existing_lower_bound_entry(methodology):
    r = _record(methodology, "npm", "lodash", "4.17.21",
               dependents="t20a_npm_lodash_dependents")
    assert r.confidence == methodology.confidence.evidence_kind["lower_bound"]
