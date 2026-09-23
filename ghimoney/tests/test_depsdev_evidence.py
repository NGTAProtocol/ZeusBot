"""Dependency Evidence from real T-19A fixtures (T-19, D-03 v2). No network."""

from __future__ import annotations

from conftest_depsdev import make_depsdev_snapshot
from ghimoney.depsdev_evidence import build_dependency_evidence, package_id
from ghimoney.models import Availability


def _by_metric(records):
    return {r.metric: r for r in records}


# --- npm: resolved graph verified (T3, T4) ----------------------------------

def test_npm_leaf_package_has_verified_zero_dependencies(methodology):
    # lodash 4.17.21: real deps.dev response is a graph with only SELF.
    # A verified HTTP 200 with an empty graph IS a legitimate zero -- this
    # is the contrast case for "404 is never zero" (D-03 condition 4).
    snap = make_depsdev_snapshot("npm", "lodash", "4.17.21",
                                 package="t1_npm_lodash_package",
                                 dependencies="t3_npm_lodash_leaf_dependencies")
    ev = _by_metric(build_dependency_evidence(snap, "npm", "lodash", "4.17.21", methodology))
    assert ev["dependency.package_found"].availability is Availability.VERIFIED
    assert ev["dependency.package_found"].raw_value is True
    assert ev["dependency.resolved_graph_direct_count"].availability is Availability.VERIFIED
    assert ev["dependency.resolved_graph_direct_count"].raw_value == 0
    assert ev["dependency.resolved_graph_total_count"].raw_value == 0


def test_npm_package_with_real_dependencies(methodology):
    # express 4.19.2: real deps.dev response (trimmed, see fixtures README):
    # 31 DIRECT + 6 INDIRECT = 37 total, excluding SELF.
    snap = make_depsdev_snapshot("npm", "express", "4.19.2",
                                 package="t1_npm_lodash_package",  # package existence only
                                 dependencies="t4_npm_express_dependencies")
    ev = _by_metric(build_dependency_evidence(snap, "npm", "express", "4.19.2", methodology))
    assert ev["dependency.resolved_graph_direct_count"].raw_value == 31
    assert ev["dependency.resolved_graph_total_count"].raw_value == 37
    assert ev["dependency.resolved_graph_direct_count"].evidence_kind == "direct_count"
    assert ev["dependency.resolved_graph_total_count"].evidence_kind == "derived"


# --- pypi and maven: resolved graph verified (T7, T9) -----------------------

def test_pypi_real_dependencies(methodology):
    snap = make_depsdev_snapshot("pypi", "requests", "2.31.0",
                                 package="t5_pypi_requests_package",
                                 dependencies="t7_pypi_requests_dependencies")
    ev = _by_metric(build_dependency_evidence(snap, "pypi", "requests", "2.31.0", methodology))
    assert ev["dependency.resolved_graph_direct_count"].raw_value == 4  # certifi, charset-normalizer, idna, urllib3
    assert ev["dependency.resolved_graph_total_count"].raw_value == 4


def test_maven_real_dependencies(methodology):
    snap = make_depsdev_snapshot("maven", "com.google.guava:guava", "32.1.3-jre",
                                 package="t8_maven_guava_package",
                                 dependencies="t9_maven_guava_dependencies")
    ev = _by_metric(build_dependency_evidence(
        snap, "maven", "com.google.guava:guava", "32.1.3-jre", methodology))
    assert ev["dependency.resolved_graph_direct_count"].raw_value == 6
    assert ev["dependency.resolved_graph_total_count"].raw_value == 6


def test_cargo_real_dependencies(methodology):
    snap = make_depsdev_snapshot("cargo", "serde", "1.0.203",
                                 package="t1_npm_lodash_package",  # existence only
                                 dependencies="t14_cargo_serde_dependencies")
    ev = _by_metric(build_dependency_evidence(snap, "cargo", "serde", "1.0.203", methodology))
    assert ev["dependency.resolved_graph_direct_count"].raw_value == 1  # serde_derive
    assert ev["dependency.resolved_graph_total_count"].raw_value == 5


# --- Go: the money test (D-03 condition 1) ----------------------------------

def test_go_resolved_graph_is_never_available_and_never_zero(methodology):
    # T12: real deps.dev response for :dependencies on Go is HTTP 404
    # "dependencies not found" -- this must be NOT_AVAILABLE, never 0.
    snap = make_depsdev_snapshot("go", "github.com/pkg/errors", "v0.9.1",
                                 package="t10_go_pkgerrors_package",
                                 requirements="t11_go_pkgerrors_requirements")
    ev = _by_metric(build_dependency_evidence(
        snap, "go", "github.com/pkg/errors", "v0.9.1", methodology))
    assert ev["dependency.resolved_graph_direct_count"].availability is Availability.NOT_AVAILABLE
    assert ev["dependency.resolved_graph_total_count"].availability is Availability.NOT_AVAILABLE
    assert ev["dependency.resolved_graph_direct_count"].raw_value is None
    assert ev["dependency.resolved_graph_total_count"].raw_value is None
    assert "not evidence of zero" in ev["dependency.resolved_graph_direct_count"].note


def test_go_declared_requirements_are_verified_and_can_be_zero(methodology):
    # T11: real deps.dev response for :requirements on Go IS available and
    # genuinely empty -- a verified zero via HTTP 200, not an inferred one.
    snap = make_depsdev_snapshot("go", "github.com/pkg/errors", "v0.9.1",
                                 package="t10_go_pkgerrors_package",
                                 requirements="t11_go_pkgerrors_requirements")
    ev = _by_metric(build_dependency_evidence(
        snap, "go", "github.com/pkg/errors", "v0.9.1", methodology))
    assert ev["dependency.declared_requirement_direct_count"].availability is Availability.VERIFIED
    assert ev["dependency.declared_requirement_direct_count"].raw_value == 0
    assert ev["dependency.declared_requirement_indirect_count"].raw_value == 0


def test_go_dependencies_404_explicitly_via_ingestion_shaped_snapshot(methodology):
    # Same as above but using the raw 404 fixture directly under the
    # "dependencies" key, as if a caller had (incorrectly) requested the
    # resolved graph for Go: still never interpreted as zero.
    snap = make_depsdev_snapshot("go", "github.com/pkg/errors", "v0.9.1",
                                 package="t10_go_pkgerrors_package",
                                 dependencies="t12_go_pkgerrors_dependencies_404")
    ev = _by_metric(build_dependency_evidence(
        snap, "go", "github.com/pkg/errors", "v0.9.1", methodology))
    # Go is excluded from RESOLVED_GRAPH_ECOSYSTEMS regardless of what key
    # is present in the snapshot: the ecosystem gate applies first.
    assert ev["dependency.resolved_graph_direct_count"].availability is Availability.NOT_AVAILABLE
    assert ev["dependency.resolved_graph_direct_count"].raw_value is None


# --- non-Go ecosystems never get parsed as requirements ---------------------

def test_npm_requirements_are_not_attempted_unverified(methodology):
    snap = make_depsdev_snapshot("npm", "lodash", "4.17.21",
                                 package="t1_npm_lodash_package",
                                 dependencies="t3_npm_lodash_leaf_dependencies")
    ev = _by_metric(build_dependency_evidence(snap, "npm", "lodash", "4.17.21", methodology))
    assert ev["dependency.declared_requirement_direct_count"].availability is Availability.NOT_AVAILABLE
    assert "not empirically verified" in ev["dependency.declared_requirement_direct_count"].note


# --- error handling (D-03 condition 4) --------------------------------------

def test_nonexistent_package_is_absence_not_error(methodology):
    snap = make_depsdev_snapshot("npm", "this-package-does-not-exist-ghimoney-test-12345",
                                 "1.0.0", package="t15_npm_nonexistent_404")
    ev = _by_metric(build_dependency_evidence(
        snap, "npm", "this-package-does-not-exist-ghimoney-test-12345", "1.0.0", methodology))
    assert ev["dependency.package_found"].availability is Availability.VERIFIED
    assert ev["dependency.package_found"].raw_value is False
    # Dependent metrics: NOT_APPLICABLE, not "0", once absence is confirmed.
    assert ev["dependency.resolved_graph_direct_count"].availability is Availability.NOT_APPLICABLE
    assert ev["dependency.declared_requirement_direct_count"].availability is Availability.NOT_APPLICABLE


def test_transport_error_on_package_propagates_as_not_available(methodology):
    from ghimoney.snapshot import Response, Snapshot
    snap = Snapshot(target="npm:x@1.0.0", source="deps-dev-api-v3", as_of="2026-09-23T12:00:00Z",
                    api_version="v3",
                    responses={"package": Response(endpoint="fixture", status=503, body="")})
    ev = _by_metric(build_dependency_evidence(snap, "npm", "x", "1.0.0", methodology))
    assert ev["dependency.package_found"].availability is Availability.NOT_AVAILABLE
    assert "transport_error" in ev["dependency.package_found"].note
    assert ev["dependency.resolved_graph_direct_count"].availability is Availability.NOT_AVAILABLE


# --- never scored, always distinct evidence version -------------------------

def test_dependency_evidence_is_never_scored(methodology):
    snap = make_depsdev_snapshot("npm", "express", "4.19.2",
                                 package="t1_npm_lodash_package",
                                 dependencies="t4_npm_express_dependencies")
    records = build_dependency_evidence(snap, "npm", "express", "4.19.2", methodology)
    assert records, "expected at least one evidence record"
    for r in records:
        assert r.normalized_value is None
        assert "not scored" in r.method
        assert r.methodology_version == "GHIM-DEPENDENCY-EVIDENCE-0.1"
        assert r.methodology_version != methodology.methodology_version


def test_confidence_reuses_methodology_table_without_duplication(methodology):
    snap = make_depsdev_snapshot("npm", "express", "4.19.2",
                                 package="t1_npm_lodash_package",
                                 dependencies="t4_npm_express_dependencies")
    ev = _by_metric(build_dependency_evidence(snap, "npm", "express", "4.19.2", methodology))
    direct = ev["dependency.resolved_graph_direct_count"]
    assert direct.confidence == methodology.confidence.evidence_kind["direct_count"]


def test_package_id_is_distinct_from_project_identity():
    assert package_id("npm", "express", "4.19.2") == "pkg:npm:express@4.19.2"


def test_provenance_has_endpoint_and_hash(methodology):
    snap = make_depsdev_snapshot("npm", "express", "4.19.2",
                                 package="t1_npm_lodash_package",
                                 dependencies="t4_npm_express_dependencies")
    ev = _by_metric(build_dependency_evidence(snap, "npm", "express", "4.19.2", methodology))
    direct = ev["dependency.resolved_graph_direct_count"]
    assert direct.provenance.source == "deps-dev-api-v3"
    assert direct.provenance.endpoints == ["fixture:t4_npm_express_dependencies"]
    assert len(direct.provenance.response_hashes) == 1
