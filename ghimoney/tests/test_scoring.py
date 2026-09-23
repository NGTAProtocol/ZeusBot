"""Aggregation rule D-02 and independence of Impact / Coverage / Confidence / Risk (D-04)."""

from __future__ import annotations

import pytest

from conftest import make_snapshot
from ghimoney.engine import analyze
from ghimoney.models import Availability, DimensionResult, ImpactStatus, RiskLevel
from ghimoney.report import render_markdown
from ghimoney.scoring import compute_confidence, compute_coverage, compute_impact


def dims(**scores):
    """Build dimension results; a score of None means the dimension is missing."""
    weights = {"adoption": .25, "dependency": .25, "maintenance": .15, "quality": .15,
               "security": .10, "community": .10}
    out = []
    for name, weight in weights.items():
        score = scores.get(name)
        out.append(DimensionResult(
            dimension=name,
            availability=Availability.VERIFIED if score is not None else Availability.NOT_AVAILABLE,
            weight=weight, score=score, metric_coverage=1.0 if score is not None else 0.0,
            confidence=0.9 if score is not None else None, metrics_used=[], metrics_missing=[]))
    return out


ALL = dict(adoption=80, dependency=70, maintenance=60, quality=50, security=40, community=30)


def test_full_coverage_is_plain_weighted_sum(methodology):
    d = dims(**ALL)
    cov = compute_coverage(d)
    imp = compute_impact(d, cov, methodology)
    assert cov.value == pytest.approx(1.0)
    assert imp.status is ImpactStatus.SCORED
    assert imp.weights_renormalized is False
    assert imp.renormalization_reason is None
    expected = .25 * 80 + .25 * 70 + .15 * 60 + .15 * 50 + .10 * 40 + .10 * 30
    assert imp.score == pytest.approx(expected)


def test_coverage_below_threshold_gives_no_score(methodology):
    d = dims(adoption=90, maintenance=90, quality=90)  # coverage 0.55
    imp = compute_impact(d, compute_coverage(d), methodology)
    assert imp.status is ImpactStatus.INSUFFICIENT_EVIDENCE
    assert imp.score is None
    assert any("coverage" in r for r in imp.reasons)


def test_renormalization_is_declared(methodology):
    # D-02 (confirmed): report must always show original weights, recalculated
    # weights, missing dimensions, and the reason for recalculation.
    d = dims(**{**ALL, "community": None})  # coverage 0.90
    cov = compute_coverage(d)
    imp = compute_impact(d, cov, methodology)
    assert imp.status is ImpactStatus.SCORED
    assert imp.weights_renormalized is True
    assert imp.missing_dimensions == ["community"]
    assert imp.original_weights["adoption"] == .25
    assert imp.effective_weights["adoption"] == pytest.approx(.25 / .90)
    assert sum(imp.effective_weights.values()) == pytest.approx(1.0)
    assert imp.renormalization_reason is not None
    assert "community" in imp.renormalization_reason


def test_both_core_dimensions_missing_blocks_score(methodology):
    # D-02 (confirmed): if both Adoption and Dependency are missing -> INSUFFICIENT_EVIDENCE.
    d = dims(maintenance=95, quality=95, security=95, community=95)
    imp = compute_impact(d, compute_coverage(d), methodology)
    assert imp.status is ImpactStatus.INSUFFICIENT_EVIDENCE
    assert imp.score is None
    assert any("core" in r for r in imp.reasons)


def test_one_core_dimension_missing_is_allowed(methodology):
    # D-02 (confirmed): at most one of the two core dimensions may be missing.
    d = dims(**{**ALL, "dependency": None})  # coverage 0.75, adoption present
    imp = compute_impact(d, compute_coverage(d), methodology)
    assert imp.status is ImpactStatus.SCORED
    assert imp.missing_dimensions == ["dependency"]


def test_single_observable_dimension_blocks_score(methodology):
    raw = methodology.model_dump()
    raw["aggregation"]["min_coverage"] = 0.0  # isolate the dimension-count rule
    m = type(methodology).model_validate(raw)
    d = dims(maintenance=99)
    imp = compute_impact(d, compute_coverage(d), m)
    assert imp.status is ImpactStatus.INSUFFICIENT_EVIDENCE
    assert any("observable dimension" in r for r in imp.reasons)


def test_one_dimension_project_cannot_look_comparable(methodology):
    # D-02 example: a project with data almost only on Maintenance must not
    # get a 90/100 comparable to a project evaluated on six dimensions.
    d = dims(maintenance=90)
    assert compute_impact(d, compute_coverage(d), methodology).score is None


def test_confidence_is_independent_of_impact(methodology):
    d = dims(**ALL)
    low = compute_confidence(d, RiskLevel.LOW, methodology)
    high = compute_confidence(d, RiskLevel.HIGH, methodology)
    assert low.base == high.base
    assert high.adjusted < low.adjusted
    assert high.risk_adjustment_factor == methodology.confidence.risk_adjustment["HIGH"]


def test_risk_never_changes_impact_or_dimension_scores(methodology):
    clean = analyze(make_snapshot(), methodology)
    risky = analyze(make_snapshot(repo_fields={"fork": True}), methodology)
    assert risky["risk"]["level"] != clean["risk"]["level"]
    assert risky["impact"] == clean["impact"]
    assert risky["dimensions"] == clean["dimensions"]
    assert risky["confidence"]["base"] == clean["confidence"]["base"]


def test_v01_real_sources_always_insufficient(methodology):
    # With GitHub only (D-03), adoption + dependency are missing: 50% coverage.
    report = analyze(make_snapshot(), methodology)
    assert report["coverage"]["value"] == pytest.approx(0.5)
    assert report["impact"]["status"] == "INSUFFICIENT_EVIDENCE"
    assert {"adoption", "dependency"} <= set(report["impact"]["missing_dimensions"])
    # Dimension-level scores remain visible for transparency.
    assert all(d["score"] is not None for d in report["dimensions"]
               if d["dimension"] not in ("adoption", "dependency"))


def _stub_report(imp, cov, conf, risk, dims_list):
    # Minimal dict with the shape engine.analyze() produces, for testing
    # report.py's rendering of the D-02 fields in isolation. Real repositories
    # never reach SCORED-with-renormalization in v0.1 (D-11): adoption and
    # dependency have no approved metrics (D-03), so they are always missing
    # and always exceed max_missing_core_dimensions. This stub exercises the
    # rendering path with synthetic dimension results instead.
    return {
        "project": {"full_name": "stub/project", "project_id": "ghp-stub", "forge_repo_id": 1},
        "methodology": {"methodology_version": "GHIM-IMPACT-0.1", "config_version": "0.1.0",
                        "config_hash": "stub", "weights_are_hypotheses": True},
        "source": {"snapshot_id": "stub", "snapshot_hash": "stub", "as_of": "2026-01-01T00:00:00Z",
                   "source_versions": {"stub": "1"}, "synthetic": True},
        "impact": imp.model_dump(mode="json"),
        "coverage": cov.model_dump(mode="json"),
        "confidence": conf.model_dump(mode="json"),
        "risk": risk.model_dump(mode="json"),
        "dimensions": [d.model_dump(mode="json") for d in dims_list],
        "evidence": [],
        "report_hash": "stub",
    }


def test_report_always_shows_weights_and_recalculation_reason(methodology):
    # D-02 (confirmed): the report must always show original weights,
    # recalculated weights, missing dimensions and the reason for recalculation.
    from ghimoney.models import RiskResult

    d = dims(**{**ALL, "community": None})
    cov = compute_coverage(d)
    imp = compute_impact(d, cov, methodology)
    conf = compute_confidence(d, RiskLevel.LOW, methodology)
    risk = RiskResult(level=RiskLevel.LOW, signals=[], checks_evaluated=[])
    assert imp.status is ImpactStatus.SCORED
    assert imp.weights_renormalized is True

    md = render_markdown(_stub_report(imp, cov, conf, risk, d))
    assert "Original weight" in md and "Recalculated weight" in md
    assert "Missing dimensions" in md and "community" in md
    assert "Reason for recalculation" in md
    assert imp.renormalization_reason in md


def test_no_partial_score_is_ever_reported_as_impact(methodology):
    """D-11 (Option 1, approved): a per-dimension or partial result must never
    surface as impact.score. With GitHub-only sources (D-03) every real
    repository is INSUFFICIENT_EVIDENCE, and that must stay a null score,
    never a "Partial Impact" substitute."""
    for snap in (make_snapshot(), make_snapshot({"community_profile": None}),
                make_snapshot(repo_fields={"stargazers_count": 50_000})):
        report = analyze(snap, methodology)
        assert report["impact"]["status"] == "INSUFFICIENT_EVIDENCE"
        assert report["impact"]["score"] is None
