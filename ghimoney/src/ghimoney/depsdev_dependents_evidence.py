"""deps.dev GetDependents Snapshot -> scored "dependency" dimension evidence
(T-20, D-12, T-20A).

Unlike T-19's Dependency Evidence (depsdev_evidence.py, always unscored by
construction), this module produces the ONE evidence metric authorized to
feed the Impact Engine's "dependency" dimension score, per D-12: dependents
(how much the ecosystem depends on the project), not outgoing dependencies.

Every record is built only from a frozen Snapshot, never a live call --
the same discipline used throughout GHIMONEY.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from ghimoney.depsdev_dependents_ingestion import DEPENDENTS_ECOSYSTEMS
from ghimoney.methodology import Methodology
from ghimoney.models import Availability, EvidenceRecord, Provenance
from ghimoney.normalization import normalize
from ghimoney.snapshot import Snapshot

METRIC_NAME = "dependents_total_count"

_PUBLIC_ONLY_NOTE = ("deps.dev counts only public dependents; per the official proto "
                    "comment, this should be treated as indicative of relative "
                    "popularity rather than a precisely accurate count (T-20A)")


@dataclass(frozen=True)
class Observation:
    availability: Availability
    value: Any = None
    kind: str | None = None
    note: str | None = None


def _classify_http_error(status: int) -> str:
    if status == 429:
        return "rate_limited"
    if 500 <= status < 600:
        return "transport_error"
    return f"unexpected_http_{status}"


def obs_dependents(snap: Snapshot, ecosystem: str) -> Observation:
    if ecosystem not in DEPENDENTS_ECOSYSTEMS:
        return Observation(
            Availability.NOT_AVAILABLE,
            note="deps.dev has no dependents data for this ecosystem (verified "
                 "empirically in T-20A on two real Go packages: HTTP 404 'dependents "
                 "not found'); a source-level limitation, not evidence of zero "
                 "dependents (D-12)")

    resp = snap.get("dependents")
    if resp is None:
        return Observation(Availability.NOT_AVAILABLE, note="no dependents request recorded")

    if resp.status == 200 and isinstance(resp.body, dict) and isinstance(
            resp.body.get("dependentCount"), int) and not isinstance(resp.body.get("dependentCount"), bool):
        value = resp.body["dependentCount"]
        if value < 0:
            return Observation(Availability.NOT_AVAILABLE,
                               note="dependents response had a negative count; "
                                    "did not match the shape verified in T-20A")
        return Observation(Availability.VERIFIED, value, "lower_bound", _PUBLIC_ONLY_NOTE)

    if resp.status == 200:
        return Observation(Availability.NOT_AVAILABLE,
                           note="dependents response did not match the shape verified "
                                "in T-20A (expected an integer 'dependentCount')")

    if resp.status == 404:
        return Observation(
            Availability.NOT_AVAILABLE,
            note="deps.dev returned 404 for dependents of a package on a supported "
                 "ecosystem; ambiguous between a nonexistent version and uncomputed "
                 "dependents -- never interpreted as zero (T-20A section 8)")

    return Observation(Availability.NOT_AVAILABLE,
                       note=f"dependents lookup failed: {_classify_http_error(resp.status)} "
                            f"(HTTP {resp.status})")


def build_dependents_evidence(snap: Snapshot, ecosystem: str, name: str, version: str,
                              methodology: Methodology) -> list[EvidenceRecord]:
    """The only evidence record authorized to feed the "dependency" dimension
    score (D-12). `methodology` must be the real, loaded scoring methodology:
    this evidence is scored using its `metrics["dependents_total_count"]`
    normalization (D-01's mechanism, applied here per D-12/T-20A), not an
    independent, unscored tag like T-19's Dependency Evidence."""
    obs = obs_dependents(snap, ecosystem)
    cfg = methodology.metrics.get(METRIC_NAME)

    normalized = None
    method = "no dependents metric defined in scoring.yaml"
    if cfg is not None:
        method = (f"{cfg.normalization}(anchor={cfg.anchor:g}) via deps.dev GetDependents "
                  "v3alpha (EXPERIMENTAL SOURCE, not v3 stable -- T-20A)")
        if obs.availability is Availability.VERIFIED:
            normalized = normalize(obs.value, cfg)

    confidence = (methodology.confidence.evidence_kind[obs.kind]
                 if obs.availability is Availability.VERIFIED and obs.kind else None)
    resp = snap.get("dependents")
    responses = [resp] if resp is not None else []
    digest = hashlib.sha256(
        f"{ecosystem}:{name}@{version}|{METRIC_NAME}|{snap.snapshot_hash}".encode())

    return [EvidenceRecord(
        evidence_id=f"dpt-{digest.hexdigest()[:16]}",
        project_id=f"pkg:{ecosystem}:{name}@{version}",
        metric=METRIC_NAME,
        availability=obs.availability,
        evidence_kind=obs.kind,
        raw_value=obs.value,
        normalized_value=normalized,
        method=method,
        confidence=confidence,
        provenance=Provenance(
            source=snap.source,
            request_keys=["dependents"] if responses else [],
            endpoints=[r.endpoint for r in responses],
            response_hashes=[r.body_hash for r in responses],
            retrieved_at=snap.as_of,
        ),
        as_of=snap.as_of,
        methodology_version=methodology.methodology_version,
        note=obs.note,
    )]
