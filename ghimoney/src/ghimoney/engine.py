"""Impact Engine pipeline: Snapshot + Methodology -> deterministic report."""

from __future__ import annotations

from typing import Any

from ghimoney import __version__
from ghimoney.canonical import sha256_json
from ghimoney.evidence import build_evidence, project_identity
from ghimoney.methodology import Methodology
from ghimoney.models import EvidenceRecord
from ghimoney.risk import assess_risk
from ghimoney.scoring import compute_confidence, compute_coverage, compute_impact, score_dimensions
from ghimoney.snapshot import Snapshot

REPORT_FORMAT = "ghimoney-report/1"


def analyze(snap: Snapshot, m: Methodology,
           extra_evidence: list[EvidenceRecord] | None = None) -> dict[str, Any]:
    """`extra_evidence` (T-20, D-12) lets a caller attach evidence from a
    second source -- today, only dependents evidence for the "dependency"
    dimension (depsdev_dependents_evidence.build_dependents_evidence).
    T-19's outgoing-dependency evidence must never be passed here (D-12)."""
    identity = project_identity(snap)
    evidence = build_evidence(snap, m, identity)
    if extra_evidence:
        evidence = evidence + list(extra_evidence)
    dimensions = score_dimensions(evidence, m)
    coverage = compute_coverage(dimensions)
    impact = compute_impact(dimensions, coverage, m)
    risk = assess_risk(evidence, identity.is_fork, m)
    confidence = compute_confidence(dimensions, risk.level, m)

    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "tool_version": __version__,
        "methodology": {
            "methodology_version": m.methodology_version,
            "config_version": m.config_version,
            "config_hash": m.config_hash,
            "weights_are_hypotheses": True,
        },
        "source": {
            "snapshot_id": snap.snapshot_id,
            "snapshot_hash": snap.snapshot_hash,
            "as_of": snap.as_of,
            "source_versions": {snap.source: snap.api_version},
            "synthetic": snap.synthetic,
        },
        "project": identity.model_dump(mode="json"),
        "impact": impact.model_dump(mode="json"),
        "coverage": coverage.model_dump(mode="json"),
        "confidence": confidence.model_dump(mode="json"),
        "risk": risk.model_dump(mode="json"),
        "dimensions": [d.model_dump(mode="json") for d in dimensions],
        "evidence": [e.model_dump(mode="json") for e in evidence],
        "roles": {
            "ai": f"not used in {m.methodology_version}",
            "human_review": "not performed: provisional, unreviewed result",
            "funding": "none: methodology 0.x results are never used for funding",
        },
    }
    report["report_hash"] = sha256_json(report)
    return report
