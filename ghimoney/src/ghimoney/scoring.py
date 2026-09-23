"""Dimension scores, Coverage, Impact and Confidence.

Each output is computed by its own function from evidence (decision D-04):
Coverage, Confidence and Risk never modify the Impact Score.
"""

from __future__ import annotations

from ghimoney.methodology import Methodology
from ghimoney.models import (
    Availability,
    ConfidenceResult,
    CoverageResult,
    DimensionResult,
    EvidenceRecord,
    ImpactResult,
    ImpactStatus,
    RiskLevel,
)


def score_dimensions(evidence: list[EvidenceRecord], m: Methodology) -> list[DimensionResult]:
    by_metric = {e.metric: e for e in evidence}
    results = []
    for dim, dcfg in m.dimensions.items():
        metrics = m.metrics_of(dim)
        if not metrics:
            # No metric can measure this dimension with the approved sources (D-03).
            results.append(DimensionResult(
                dimension=dim, availability=Availability.NOT_AVAILABLE, weight=dcfg.weight,
                score=None, metric_coverage=0.0, confidence=None, metrics_used=[],
                metrics_missing=[]))
            continue
        used = {n: c for n, c in metrics.items()
                if n in by_metric and by_metric[n].availability is Availability.VERIFIED}
        missing = sorted(set(metrics) - set(used))
        coverage = sum(c.weight for c in used.values())
        if not used or coverage < m.aggregation.min_dimension_metric_coverage:
            results.append(DimensionResult(
                dimension=dim, availability=Availability.INSUFFICIENT_EVIDENCE,
                weight=dcfg.weight, score=None, metric_coverage=coverage, confidence=None,
                metrics_used=sorted(used), metrics_missing=missing))
            continue
        score = sum(c.weight * by_metric[n].normalized_value for n, c in used.items()) / coverage
        confidence = sum(c.weight * by_metric[n].confidence for n, c in used.items()) / coverage
        results.append(DimensionResult(
            dimension=dim, availability=Availability.VERIFIED, weight=dcfg.weight, score=score,
            metric_coverage=coverage, confidence=confidence, metrics_used=sorted(used),
            metrics_missing=missing))
    return results


def _observable(dims: list[DimensionResult]) -> list[DimensionResult]:
    return [d for d in dims if d.availability is Availability.VERIFIED]


def compute_coverage(dims: list[DimensionResult]) -> CoverageResult:
    applicable = [d for d in dims if d.availability is not Availability.NOT_APPLICABLE]
    observable = _observable(applicable)
    total = sum(d.weight for d in applicable)
    return CoverageResult(
        value=sum(d.weight for d in observable) / total if total else 0.0,
        observable_dimensions=[d.dimension for d in observable],
        missing_dimensions=[d.dimension for d in applicable if d not in observable],
    )


def compute_impact(dims: list[DimensionResult], coverage: CoverageResult,
                   m: Methodology) -> ImpactResult:
    """Aggregation rule D-02."""
    agg = m.aggregation
    observable = _observable(dims)
    original = {d.dimension: d.weight for d in dims}
    missing_core = [d for d in coverage.missing_dimensions if m.dimensions[d].core]

    reasons = []
    if coverage.value < agg.min_coverage:
        reasons.append(f"coverage {coverage.value:.2f} below minimum {agg.min_coverage:.2f}")
    if len(observable) < agg.min_observable_dimensions:
        reasons.append(f"{len(observable)} observable dimension(s), minimum "
                       f"{agg.min_observable_dimensions}")
    if len(missing_core) > agg.max_missing_core_dimensions:
        reasons.append(f"{len(missing_core)} core dimension(s) missing ({', '.join(missing_core)}), "
                       f"maximum {agg.max_missing_core_dimensions}")

    if reasons:
        return ImpactResult(
            status=ImpactStatus.INSUFFICIENT_EVIDENCE, score=None, reasons=reasons,
            original_weights=original, effective_weights={}, weights_renormalized=False,
            missing_dimensions=coverage.missing_dimensions)

    total = sum(d.weight for d in observable)
    effective = {d.dimension: d.weight / total for d in observable}
    return ImpactResult(
        status=ImpactStatus.SCORED,
        score=sum(effective[d.dimension] * d.score for d in observable),
        reasons=[],
        original_weights=original,
        effective_weights=effective,
        weights_renormalized=bool(coverage.missing_dimensions),
        missing_dimensions=coverage.missing_dimensions,
    )


def compute_confidence(dims: list[DimensionResult], risk_level: RiskLevel,
                       m: Methodology) -> ConfidenceResult:
    observable = _observable(dims)
    factor = m.confidence.risk_adjustment[risk_level.value]
    if not observable:
        return ConfidenceResult(base=None, risk_adjustment_factor=factor, adjusted=None)
    total = sum(d.weight for d in observable)
    base = sum(d.weight * d.confidence for d in observable) / total
    return ConfidenceResult(base=base, risk_adjustment_factor=factor, adjusted=base * factor)
