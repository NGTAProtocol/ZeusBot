"""deps.dev Snapshot -> Dependency Evidence Records (T-19, D-03 v2).

Every record here is produced only from a frozen Snapshot, never from a live
call -- the same discipline already used for GitHub (see evidence.py). None
of it is scored: config/scoring.yaml defines no metric for the "dependency"
dimension (deliberately, per D-03 v1/v2), so `normalized_value` is always
None here and `method` says so explicitly. This module is not called from
ghimoney.engine.analyze(): wiring Dependency Evidence into the Impact Engine
is T-20, not attempted here.

D-03 v2's mandatory conditions this module implements:
  1. Ecosystem coverage is differentiated, not assumed: Go is NOT_AVAILABLE
     for the resolved graph, never "0" (see obs_resolved_graph).
  2. `relatedProjects[*].relationProvenance == "UNVERIFIED_METADATA"` from
     deps.dev is never upgraded to a verified relation by this module (it is
     simply not read/used here; nothing in this module claims a project
     link is verified).
  3. Reproducibility: everything here reads only from the Snapshot passed
     in, never from the network.
  4. A 404 is never read as "0 dependencies": see the explicit branches in
     obs_resolved_graph / obs_declared_requirements below.
  5. No rate limit assumption: this module does not retry or rate-limit
     itself; it only classifies whatever HTTP status it is given.
  6. Attribution/licensing is not evaluated by this module (out of scope
     for evidence extraction); see DECISIONS.md D-03 condition 6.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from ghimoney.depsdev_ingestion import RESOLVED_GRAPH_ECOSYSTEMS
from ghimoney.methodology import Methodology
from ghimoney.models import Availability, EvidenceRecord, Provenance
from ghimoney.snapshot import Snapshot

# Independent of GHIM-IMPACT-0.1 on purpose: this evidence format can evolve
# (e.g. once T-20 designs how it feeds the Impact Engine) without implying
# that the scoring methodology itself changed.
EVIDENCE_VERSION = "GHIM-DEPENDENCY-EVIDENCE-0.1"

UNSCORED_METHOD = ("signal: recorded, not scored "
                   "(no dependency metric defined in scoring.yaml, D-03)")


@dataclass(frozen=True)
class Observation:
    availability: Availability
    value: Any = None
    kind: str | None = None
    keys: tuple[str, ...] = ()
    note: str | None = None


def package_id(ecosystem: str, name: str, version: str) -> str:
    """Package identity. Deliberately distinct from a GHIMONEY Project
    Identity (Directive §5, ghimoney.evidence.project_identity): correlating
    a deps.dev package to a GHIMONEY project is future work, not attempted
    here."""
    return f"pkg:{ecosystem}:{name}@{version}"


def _classify_http_error(status: int) -> str:
    if status == 429:
        return "rate_limited"
    if 500 <= status < 600:
        return "transport_error"
    return f"unexpected_http_{status}"


def obs_package_found(snap: Snapshot) -> Observation:
    resp = snap.get("package")
    if resp is None:
        return Observation(Availability.NOT_AVAILABLE, note="no package request recorded")
    if resp.status == 200:
        return Observation(Availability.VERIFIED, True, "presence_check", ("package",))
    if resp.status == 404:
        return Observation(Availability.VERIFIED, False, "absence_check", ("package",),
                           "package not found on deps.dev for this ecosystem "
                           "(a real absence, not a transport error)")
    return Observation(Availability.NOT_AVAILABLE, keys=("package",),
                       note=f"package lookup failed: {_classify_http_error(resp.status)} "
                            f"(HTTP {resp.status})")


def _propagate_from_package(package_found: Observation) -> Observation | None:
    """Shared gating for anything that depends on the package existing.
    Returns an Observation to short-circuit with, or None to continue."""
    if package_found.availability is Availability.VERIFIED and package_found.value is False:
        return Observation(Availability.NOT_APPLICABLE,
                           note="package does not exist on deps.dev: dependency data "
                                "does not apply")
    if package_found.availability is not Availability.VERIFIED:
        return Observation(Availability.NOT_AVAILABLE,
                           note="package existence could not be confirmed; "
                                "dependency data was not attempted")
    return None


def _resolved_graph_counts(nodes: list[dict]) -> tuple[int, int]:
    direct = sum(1 for n in nodes if n.get("relation") == "DIRECT")
    total = sum(1 for n in nodes if n.get("relation") in ("DIRECT", "INDIRECT"))
    return direct, total


def obs_resolved_graph(snap: Snapshot, ecosystem: str,
                       package_found: Observation) -> tuple[Observation, Observation]:
    """(direct_count, total_count) for the resolved dependency graph.

    D-03 condition 1: Go is always NOT_AVAILABLE here, never "0" -- deps.dev
    has no resolved graph for Go (T-19A T12: HTTP 404 for a real package).
    """
    if ecosystem not in RESOLVED_GRAPH_ECOSYSTEMS:
        na = Observation(
            Availability.NOT_AVAILABLE,
            note="deps.dev has no resolved dependency graph for this ecosystem "
                 "(verified empirically in T-19A: HTTP 404 'dependencies not found' "
                 "for Go); a source-level limitation, not evidence of zero "
                 "dependencies (D-03 condition 1)")
        return na, na

    gated = _propagate_from_package(package_found)
    if gated is not None:
        return gated, gated

    resp = snap.get("dependencies")
    if resp is None:
        na = Observation(Availability.NOT_AVAILABLE, note="no dependencies request recorded")
        return na, na
    if resp.status == 200 and isinstance(resp.body, dict) and isinstance(resp.body.get("nodes"), list):
        direct, total = _resolved_graph_counts(resp.body["nodes"])
        return (Observation(Availability.VERIFIED, direct, "direct_count", ("dependencies",)),
                Observation(Availability.VERIFIED, total, "derived", ("dependencies",)))
    if resp.status == 404:
        na = Observation(
            Availability.NOT_AVAILABLE, keys=("dependencies",),
            note="deps.dev returned 404 for the resolved dependency graph of a package "
                 "that exists on this ecosystem; ambiguous between a nonexistent version "
                 "and an uncomputed graph -- never interpreted as zero dependencies "
                 "(D-03 condition 4)")
        return na, na
    na = Observation(Availability.NOT_AVAILABLE, keys=("dependencies",),
                     note=f"dependency graph lookup failed: "
                          f"{_classify_http_error(resp.status)} (HTTP {resp.status})")
    return na, na


def _go_requirement_counts(body: Any) -> tuple[int, int] | None:
    """Only Go's GetRequirements shape was empirically verified in T-19A T11
    (`{"go": {"directDependencies": [...], "indirectDependencies": [...]}}`).
    Returns None if the body does not match that verified shape."""
    if not isinstance(body, dict):
        return None
    section = body.get("go")
    if not isinstance(section, dict):
        return None
    direct, indirect = section.get("directDependencies"), section.get("indirectDependencies")
    if not isinstance(direct, list) or not isinstance(indirect, list):
        return None
    return len(direct), len(indirect)


def obs_declared_requirements(snap: Snapshot, ecosystem: str,
                              package_found: Observation) -> tuple[Observation, Observation]:
    """(direct_count, indirect_count) from declared requirements.

    Restricted to Go: the only ecosystem whose GetRequirements response
    shape T-19A empirically verified (T11). Other ecosystems are
    NOT_AVAILABLE here rather than parsed on an unverified assumption about
    their response shape -- their Dependency Evidence instead comes from
    the resolved graph (obs_resolved_graph), which was verified for them.
    Package existence is checked first: if the package itself is confirmed
    absent, that is the reason ("does not apply"), not the ecosystem's
    unverified response shape.
    """
    gated = _propagate_from_package(package_found)
    if gated is not None:
        return gated, gated

    if ecosystem != "go":
        na = Observation(
            Availability.NOT_AVAILABLE,
            note="GetRequirements response shape was not empirically verified for this "
                 "ecosystem in T-19A (only Go was, T11); not parsed to avoid an "
                 "unverified assumption")
        return na, na

    resp = snap.get("requirements")
    if resp is None:
        na = Observation(Availability.NOT_AVAILABLE, note="no requirements request recorded")
        return na, na
    if resp.status == 200:
        counts = _go_requirement_counts(resp.body)
        if counts is not None:
            direct, indirect = counts
            return (Observation(Availability.VERIFIED, direct, "direct_count", ("requirements",)),
                    Observation(Availability.VERIFIED, indirect, "direct_count", ("requirements",)))
        na = Observation(Availability.NOT_AVAILABLE, keys=("requirements",),
                         note="requirements response did not match the shape verified "
                              "in T-19A T11")
        return na, na
    if resp.status == 404:
        na = Observation(
            Availability.NOT_AVAILABLE, keys=("requirements",),
            note="deps.dev returned 404 for declared requirements of a package that "
                 "exists on this ecosystem; ambiguous between a nonexistent version and "
                 "missing data -- never interpreted as zero requirements "
                 "(D-03 condition 4)")
        return na, na
    na = Observation(Availability.NOT_AVAILABLE, keys=("requirements",),
                     note=f"requirements lookup failed: "
                          f"{_classify_http_error(resp.status)} (HTTP {resp.status})")
    return na, na


def build_dependency_evidence(snap: Snapshot, ecosystem: str, name: str, version: str,
                              methodology: Methodology) -> list[EvidenceRecord]:
    """Snapshot -> Dependency Evidence Records for one (ecosystem, package,
    version). `methodology` is read only for its `confidence.evidence_kind`
    table (reused as-is, not duplicated); its dimensions/metrics/aggregation
    are untouched and irrelevant here, since scoring.yaml defines no metric
    for "dependency" (D-03)."""
    pkg_id = package_id(ecosystem, name, version)
    package_found = obs_package_found(snap)
    direct_graph, total_graph = obs_resolved_graph(snap, ecosystem, package_found)
    direct_req, indirect_req = obs_declared_requirements(snap, ecosystem, package_found)

    named = {
        "dependency.package_found": package_found,
        "dependency.resolved_graph_direct_count": direct_graph,
        "dependency.resolved_graph_total_count": total_graph,
        "dependency.declared_requirement_direct_count": direct_req,
        "dependency.declared_requirement_indirect_count": indirect_req,
    }

    records = []
    for metric, obs in sorted(named.items()):
        responses = [snap.get(k) for k in obs.keys if snap.get(k) is not None]
        confidence = (methodology.confidence.evidence_kind[obs.kind]
                     if obs.availability is Availability.VERIFIED and obs.kind else None)
        digest = hashlib.sha256(f"{pkg_id}|{metric}|{snap.snapshot_hash}".encode())
        records.append(EvidenceRecord(
            evidence_id=f"ddv-{digest.hexdigest()[:16]}",
            project_id=pkg_id,
            metric=metric,
            availability=obs.availability,
            evidence_kind=obs.kind,
            raw_value=obs.value,
            normalized_value=None,
            method=UNSCORED_METHOD,
            confidence=confidence,
            provenance=Provenance(
                source=snap.source,
                request_keys=list(obs.keys),
                endpoints=[r.endpoint for r in responses],
                response_hashes=[r.body_hash for r in responses],
                retrieved_at=snap.as_of,
            ),
            as_of=snap.as_of,
            methodology_version=EVIDENCE_VERSION,
            note=obs.note,
        ))
    return records
