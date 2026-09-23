"""T-20: Full Impact Score with dependents feeding the "dependency" dimension
(D-12), via engine.analyze(snap, m, extra_evidence=...). No network."""

from __future__ import annotations

import pytest

from conftest import make_snapshot
from conftest_depsdev import make_dependents_snapshot
from ghimoney.depsdev_dependents_evidence import build_dependents_evidence
from ghimoney.engine import analyze
from ghimoney.models import Availability, DimensionResult, ImpactStatus
from ghimoney.scoring import compute_coverage, compute_impact

WEIGHTS = {"adoption": .25, "dependency": .25, "maintenance": .15, "quality": .15,
          "security": .10, "community": .10}


def dims(**scores) -> list[DimensionResult]:
    out = []
    for name, weight in WEIGHTS.items():
        score = scores.get(name)
        out.append(DimensionResult(
            dimension=name,
            availability=Availability.VERIFIED if score is not None else Availability.NOT_AVAILABLE,
            weight=weight, score=score, metric_coverage=1.0 if score is not None else 0.0,
            confidence=0.9 if score is not None else None, metrics_used=[], metrics_missing=[]))
    return out


def dependents_evidence(methodology, count: int, ecosystem="npm", name="pkg", version="1.0.0",
                        status: int = 200):
    from ghimoney.snapshot import Response, Snapshot
    body = {"dependentCount": count} if status == 200 else "dependents not found"
    snap = Snapshot(target=f"{ecosystem}:{name}@{version}",
                    source="deps-dev-api-v3alpha-dependents", as_of="2026-09-23T12:00:00Z",
                    api_version="v3alpha",
                    responses={"dependents": Response(endpoint="fixture", status=status, body=body)})
    return build_dependents_evidence(snap, ecosystem, name, version, methodology)


# --- 1. Full Impact Score with all dimensions available ---------------------

def test_full_impact_score_all_dimensions_available(methodology):
    d = dims(adoption=80, dependency=70, maintenance=60, quality=50, security=40, community=30)
    cov = compute_coverage(d)
    imp = compute_impact(d, cov, methodology)
    assert imp.status is ImpactStatus.SCORED
    assert imp.weights_renormalized is False
    expected = .25 * 80 + .25 * 70 + .15 * 60 + .15 * 50 + .10 * 40 + .10 * 30
    assert imp.score == pytest.approx(expected)


def test_dependency_dimension_scores_from_real_dependents_evidence(methodology):
    # lodash's real T-20A dependent count (22,623) saturates well above the
    # config-declared anchor -> dimension score is 100.
    from conftest_depsdev import make_dependents_snapshot as mk
    snap = mk("npm", "lodash", "4.17.21", dependents="t20a_npm_lodash_dependents")
    evidence = build_dependents_evidence(snap, "npm", "lodash", "4.17.21", methodology)
    from ghimoney.scoring import score_dimensions
    result = {r.dimension: r for r in score_dimensions(evidence, methodology)}
    assert result["dependency"].availability is Availability.VERIFIED
    assert result["dependency"].score == 100.0
    assert result["adoption"].availability is Availability.NOT_AVAILABLE  # still no source


# --- 2. Renormalization with missing dimensions -----------------------------

def test_renormalization_with_dependency_present_and_adoption_missing(methodology):
    d = dims(dependency=70, maintenance=60, quality=50, security=40, community=30)  # coverage .75
    cov = compute_coverage(d)
    imp = compute_impact(d, cov, methodology)
    assert imp.status is ImpactStatus.SCORED
    assert imp.weights_renormalized is True
    assert imp.missing_dimensions == ["adoption"]
    assert imp.effective_weights["dependency"] == pytest.approx(.25 / .75)
    assert sum(imp.effective_weights.values()) == pytest.approx(1.0)
    assert imp.renormalization_reason is not None and "adoption" in imp.renormalization_reason


# --- 3. Dependency NOT_AVAILABLE (Go, per D-12) -----------------------------

def test_go_dependency_not_available_via_engine_integration(methodology):
    github_snap = make_snapshot()
    extra = dependents_evidence(methodology, count=0, status=404, ecosystem="go",
                                name="github.com/pkg/errors", version="v0.9.1")
    report = analyze(github_snap, methodology, extra_evidence=extra)
    # Evidence layer (D-12): the dependents record itself is NOT_AVAILABLE.
    ev = next(e for e in report["evidence"] if e["metric"] == "dependents_total_count")
    assert ev["availability"] == "NOT_AVAILABLE"
    assert ev["raw_value"] is None
    # Dimension layer (D-02, unchanged): a defined metric with zero verified
    # coverage is INSUFFICIENT_EVIDENCE, not NOT_AVAILABLE -- same existing
    # rule already applied to every other dimension. Either way, never a
    # numeric score.
    dep = next(d for d in report["dimensions"] if d["dimension"] == "dependency")
    assert dep["availability"] == "INSUFFICIENT_EVIDENCE"
    assert dep["score"] is None


# --- 4. Dependency UNKNOWN-equivalent (missing dependents request) ---------

def test_dependency_not_available_when_dependents_never_requested(methodology):
    # No extra_evidence at all: no "dependents_total_count" evidence record
    # exists (not even a NOT_AVAILABLE one) -- zero verified coverage of the
    # dimension's one metric, same INSUFFICIENT_EVIDENCE outcome as above,
    # via existing D-02 logic. Never a numeric score.
    report = analyze(make_snapshot(), methodology)
    assert not any(e["metric"] == "dependents_total_count" for e in report["evidence"])
    dep = next(d for d in report["dimensions"] if d["dimension"] == "dependency")
    assert dep["availability"] == "INSUFFICIENT_EVIDENCE"
    assert dep["score"] is None


# --- 5. Coverage insufficient ------------------------------------------------

def test_coverage_insufficient_even_with_dependency_verified(methodology):
    # Only dependency + maintenance verified: 2 dimensions but coverage
    # .25+.15=.40 < 0.60 -> still INSUFFICIENT_EVIDENCE (D-02 unchanged).
    d = dims(dependency=90, maintenance=90)
    cov = compute_coverage(d)
    imp = compute_impact(d, cov, methodology)
    assert imp.status is ImpactStatus.INSUFFICIENT_EVIDENCE
    assert imp.score is None
    assert any("coverage" in r for r in imp.reasons)


# --- 6. Missing data never becomes zero -------------------------------------

def test_dependency_missing_is_not_scored_as_zero(methodology):
    d = dims(adoption=80, maintenance=60, quality=50, security=40, community=30)  # no dependency
    cov = compute_coverage(d)
    imp = compute_impact(d, cov, methodology)
    # dependency excluded from the weighted sum entirely, not counted as 0.
    assert "dependency" not in imp.effective_weights
    assert imp.missing_dimensions == ["dependency"]


def test_full_engine_report_never_shows_dependency_as_zero_on_404(methodology):
    extra = dependents_evidence(methodology, count=0, status=404)
    report = analyze(make_snapshot(), methodology, extra_evidence=extra)
    ev = next(e for e in report["evidence"] if e["metric"] == "dependents_total_count")
    assert ev["raw_value"] is None
    assert ev["availability"] == "NOT_AVAILABLE"


# --- 7. Stars/forks cannot alter the score (Rule 2, regression) ------------

def test_stars_and_forks_still_cannot_alter_score_with_dependents_wired(methodology):
    extra = dependents_evidence(methodology, count=22623)
    honest = analyze(make_snapshot(), methodology, extra_evidence=extra)
    inflated = analyze(make_snapshot(repo_fields={"stargazers_count": 250_000,
                                                  "forks_count": 40_000}),
                       methodology, extra_evidence=extra)
    assert inflated["impact"] == honest["impact"]
    assert inflated["dimensions"] == honest["dimensions"]


def test_dependent_count_itself_is_not_a_star_proxy(methodology):
    # A genuine dependents count is not "stars": verify the metric name and
    # source are distinct from any GitHub popularity signal.
    extra = dependents_evidence(methodology, count=22623)
    assert extra[0].metric == "dependents_total_count"
    assert extra[0].provenance.source == "deps-dev-api-v3alpha-dependents"


# --- 8. Regression: existing GitHub-only behaviour is unaffected -----------

def test_github_only_analysis_unaffected_when_no_extra_evidence(methodology):
    report = analyze(make_snapshot(), methodology)
    assert report["coverage"]["value"] == pytest.approx(0.5)
    assert report["impact"]["status"] == "INSUFFICIENT_EVIDENCE"
