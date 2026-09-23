"""Unit tests: normalization, methodology, evidence extraction, missing data (Rule 3)."""

from __future__ import annotations

import math

import pytest
import yaml

from conftest import commit, make_snapshot
from ghimoney.evidence import build_evidence, observe_all, project_identity
from ghimoney.methodology import DEFAULT_CONFIG, Methodology, MetricConfig
from ghimoney.models import Availability
from ghimoney.normalization import normalize


# --- normalization (D-01) ----------------------------------------------------

def test_log_saturating_anchor_and_bounds():
    cfg = MetricConfig(dimension="x", weight=1, normalization="log_saturating", anchor=100)
    assert normalize(0, cfg) == 0.0
    assert normalize(100, cfg) == pytest.approx(100.0)
    assert normalize(10**6, cfg) == 100.0
    assert normalize(10, cfg) == pytest.approx(100 * math.log1p(10) / math.log1p(100))


def test_log_scale_damps_extremes():
    cfg = MetricConfig(dimension="x", weight=1, normalization="log_saturating", anchor=1000)
    # A 10x larger value gains far less than 10x the score.
    assert normalize(100, cfg) / normalize(10, cfg) < 2.0


def test_log_decay():
    cfg = MetricConfig(dimension="x", weight=1, normalization="log_decay", anchor=365)
    assert normalize(0, cfg) == 100.0
    assert normalize(365, cfg) == pytest.approx(0.0)
    assert normalize(5000, cfg) == 0.0
    assert normalize(30, cfg) > normalize(200, cfg)


def test_normalization_rejects_bad_input():
    frac = MetricConfig(dimension="x", weight=1, normalization="fraction")
    boolean = MetricConfig(dimension="x", weight=1, normalization="boolean")
    log = MetricConfig(dimension="x", weight=1, normalization="log_saturating", anchor=10)
    with pytest.raises(ValueError):
        normalize(1.5, frac)
    with pytest.raises(TypeError):
        normalize(1, boolean)
    with pytest.raises(TypeError):
        normalize(None, log)
    with pytest.raises(ValueError):
        normalize(-1, log)


def test_log_normalization_requires_anchor():
    with pytest.raises(ValueError):
        MetricConfig(dimension="x", weight=1, normalization="log_saturating")


# --- methodology -------------------------------------------------------------

def _raw_config():
    return yaml.safe_load(DEFAULT_CONFIG.read_text())


def test_methodology_loads_and_is_versioned(methodology):
    assert methodology.methodology_version == "GHIM-IMPACT-0.2"
    assert len(methodology.config_hash) == 64


def test_adoption_has_no_metrics(methodology):
    # D-03: v0.1 is GitHub only; adoption has no verified source and must
    # stay NOT_AVAILABLE, never scored.
    assert methodology.metrics_of("adoption") == {}


def test_dependency_has_exactly_the_dependents_metric(methodology):
    # D-12/T-20: "dependency" is scored only from dependents evidence
    # (depsdev_dependents_evidence.py); T-19's outgoing-dependency evidence
    # must never appear here.
    metrics = methodology.metrics_of("dependency")
    assert set(metrics) == {"dependents_total_count"}
    assert metrics["dependents_total_count"].weight == 1.0


def test_popularity_is_never_a_scored_metric(methodology):
    # Rule 2: stars / forks / watchers are evidence, not value.
    for name in methodology.metrics:
        assert not any(w in name for w in ("star", "fork", "subscriber", "watcher"))


def test_dimension_weights_must_sum_to_one():
    raw = _raw_config()
    raw["dimensions"]["adoption"]["weight"] = 0.5
    with pytest.raises(ValueError, match="sum to 1.0"):
        Methodology.model_validate(raw)


def test_unknown_config_keys_are_rejected():
    raw = _raw_config()
    raw["aggregation"]["surprise"] = 1
    with pytest.raises(ValueError):
        Methodology.model_validate(raw)


def test_config_hash_changes_with_any_parameter(methodology):
    raw = _raw_config()
    raw["metrics"]["commits_last_365d"]["anchor"] = 501
    assert Methodology.model_validate(raw).config_hash != methodology.config_hash


# --- evidence and missing data (Rule 3) --------------------------------------

def test_identity_is_anchored_to_numeric_repo_id():
    a = project_identity(make_snapshot())
    renamed = project_identity(make_snapshot(repo_fields={"full_name": "new-owner/renamed"}))
    other = project_identity(make_snapshot(repo_fields={"id": 999}))
    assert a.project_id == renamed.project_id
    assert a.project_id != other.project_id


def test_empty_repository(methodology):
    obs = observe_all(make_snapshot({
        "latest_commit": {"status": 409, "body": {"message": "Git Repository is empty."}},
        "commits_window": {"status": 409, "body": {"message": "Git Repository is empty."}},
        "contributors": {"status": 204, "body": None},
    }), methodology)
    assert obs["commits_last_365d"].availability is Availability.VERIFIED
    assert obs["commits_last_365d"].value == 0
    assert obs["days_since_last_commit"].availability is Availability.NOT_APPLICABLE
    assert obs["total_contributors"].value == 0


def test_no_releases_is_unknown_not_zero(methodology):
    obs = observe_all(make_snapshot({"releases": {"status": 200, "body": []}}), methodology)
    assert obs["releases_last_365d"].availability is Availability.UNKNOWN
    assert obs["releases_last_365d"].value is None


def test_no_workflows_is_unknown_not_zero(methodology):
    obs = observe_all(make_snapshot(
        {"workflows": {"status": 200, "body": {"total_count": 0, "workflows": []}}}), methodology)
    assert obs["ci_workflows_present"].availability is Availability.UNKNOWN


def test_security_policy_absent_vs_unavailable(methodology):
    absent = observe_all(make_snapshot({
        "security_policy:SECURITY.md": {"status": 404, "body": None}}), methodology)
    assert absent["security_policy_present"].availability is Availability.VERIFIED
    assert absent["security_policy_present"].value is False
    assert absent["security_policy_present"].kind == "absence_check"

    failed = observe_all(make_snapshot({
        "security_policy:SECURITY.md": {"status": 404, "body": None},
        "security_policy:docs/SECURITY.md": {"status": 403, "body": None}}), methodology)
    assert failed["security_policy_present"].availability is Availability.NOT_AVAILABLE


def test_community_profile_counts_present_files(methodology):
    # Base fixture: readme, license, contributing, issue_template present (4 of 6).
    obs = observe_all(make_snapshot(), methodology)["community_profile_files"]
    assert obs.value == pytest.approx(4 / 6, abs=1e-4)
    only_coc_file = make_snapshot({"community_profile": {"status": 200, "body": {"files": {
        "code_of_conduct": None, "code_of_conduct_file": {}}}}})
    assert observe_all(only_coc_file, methodology)["community_profile_files"].value == \
        pytest.approx(1 / 6, abs=1e-4)


def test_api_failure_is_not_available(methodology):
    obs = observe_all(make_snapshot({"contributors": {"status": 403, "body": {}}}), methodology)
    assert obs["total_contributors"].availability is Availability.NOT_AVAILABLE
    assert obs["total_contributors"].value is None


def test_missing_response_is_not_available(methodology):
    obs = observe_all(make_snapshot({"community_profile": None}), methodology)
    assert obs["community_profile_files"].availability is Availability.NOT_AVAILABLE


def test_truncated_pagination_is_lower_bound(methodology):
    snap = make_snapshot({"contributors": {"status": 200, "body": [{}] * 500,
                                           "pages": 5, "truncated": True}})
    obs = observe_all(snap, methodology)["total_contributors"]
    assert obs.kind == "lower_bound"
    ev = {e.metric: e for e in build_evidence(snap, methodology, project_identity(snap))}
    assert ev["total_contributors"].confidence == methodology.confidence.evidence_kind["lower_bound"]


def test_authors_without_login_are_counted_by_email_hash(methodology):
    commits = [commit(1, None, "a@x.invalid"), commit(2, None, "a@x.invalid"),
               commit(3, None, "b@x.invalid"), commit(4, "dev")]
    obs = observe_all(make_snapshot({"commits_window": {"status": 200, "body": commits}}),
                      methodology)
    assert obs["distinct_authors_last_365d"].value == 3


def test_evidence_has_provenance(snapshot, methodology):
    for e in build_evidence(snapshot, methodology, project_identity(snapshot)):
        assert e.provenance.request_keys, e.metric
        assert len(e.provenance.response_hashes) == len(e.provenance.endpoints)
        assert e.as_of == snapshot.as_of
        assert e.methodology_version == "GHIM-IMPACT-0.2"
        if e.availability is Availability.VERIFIED:
            assert e.confidence is not None
        else:
            assert e.normalized_value is None and e.confidence is None
