"""deps.dev ingestion against a mocked transport (T-19). No real network use."""

from __future__ import annotations

import httpx
import pytest

from ghimoney.depsdev_ingestion import (
    DepsDevIngestionError,
    DepsDevIngestor,
    validate_ecosystem,
    validate_package,
)

# httpx normalizes .url.path back to unescaped characters (e.g. "%2F" -> "/"),
# so handlers match on the decoded path; the percent-encoding itself is
# checked separately via .url.raw_path (see the two encoding tests below).
CALLS: list[str] = []


def handler(request: httpx.Request) -> httpx.Response:
    CALLS.append(request.url.raw_path.decode())
    path = request.url.path
    if path == "/v3/systems/npm/packages/express":
        return httpx.Response(200, json={"packageKey": {"system": "NPM", "name": "express"}})
    if path == "/v3/systems/npm/packages/express/versions/4.19.2:dependencies":
        return httpx.Response(200, json={"nodes": [], "edges": [], "error": ""})
    if path == "/v3/systems/go/packages/github.com/pkg/errors":
        return httpx.Response(200, json={"packageKey": {"system": "GO"}})
    if path == "/v3/systems/go/packages/github.com/pkg/errors/versions/v0.9.1:requirements":
        return httpx.Response(200, json={"go": {"directDependencies": []}})
    if path == "/v3/systems/npm/packages/nonexistent":
        return httpx.Response(404, text="package not found")
    if path == "/v3/systems/maven/packages/com.google.guava:guava":
        return httpx.Response(200, json={"packageKey": {"system": "MAVEN"}})
    if path == "/v3/systems/maven/packages/com.google.guava:guava/versions/32.1.3-jre:dependencies":
        return httpx.Response(200, json={"nodes": [], "edges": [], "error": ""})
    return httpx.Response(500, text=f"unexpected path in test: {path!r}")


def mock_ingestor() -> DepsDevIngestor:
    CALLS.clear()
    client = httpx.Client(base_url="https://api.deps.dev", transport=httpx.MockTransport(handler))
    return DepsDevIngestor(client)


def test_npm_uses_resolved_dependency_graph():
    snap = mock_ingestor().fetch("npm", "express", "4.19.2")
    assert snap.get("package").status == 200
    assert snap.get("dependencies") is not None
    assert snap.get("requirements") is None
    assert snap.target == "npm:express@4.19.2"


def test_go_uses_requirements_not_dependencies():
    # T-19A/D-03 condition 1: Go has no resolved graph endpoint; the
    # ingestor must not even call :dependencies for Go.
    snap = mock_ingestor().fetch("go", "github.com/pkg/errors", "v0.9.1")
    assert snap.get("requirements") is not None
    assert snap.get("dependencies") is None
    assert "/versions/v0.9.1:dependencies" not in "".join(CALLS)


def test_nonexistent_package_short_circuits():
    ingestor = mock_ingestor()
    snap = ingestor.fetch("npm", "nonexistent", "1.0.0")
    assert snap.get("package").status == 404
    # No dependencies/requirements call was attempted once the package
    # itself was confirmed absent.
    assert snap.get("dependencies") is None
    assert snap.get("requirements") is None
    assert len(CALLS) == 1


def test_maven_group_artifact_is_percent_encoded():
    snap = mock_ingestor().fetch("maven", "com.google.guava:guava", "32.1.3-jre")
    assert snap.get("package").status == 200
    assert snap.get("dependencies").status == 200
    assert any("com.google.guava%3Aguava" in c for c in CALLS)


def test_go_module_path_is_percent_encoded():
    mock_ingestor().fetch("go", "github.com/pkg/errors", "v0.9.1")
    # CALLS holds raw_path (undecoded wire form): the module path's slashes
    # must be percent-encoded, or deps.dev would see extra path segments.
    assert any("github.com%2Fpkg%2Ferrors" in c for c in CALLS)


def test_fetch_is_reproducible():
    a = mock_ingestor().fetch("npm", "express", "4.19.2")
    b = mock_ingestor().fetch("npm", "express", "4.19.2", as_of=None)
    # as_of differs only by real wall-clock time in this test; force equal
    # as_of to compare response content deterministically.
    from dataclasses import replace
    b2 = replace(b, as_of=a.as_of)
    assert a.snapshot_hash == b2.snapshot_hash


@pytest.mark.parametrize("ecosystem", ["composer", "rubygems", "nuget", "", "NPM"])
def test_unsupported_ecosystem_is_rejected(ecosystem):
    # rubygems/nuget exist on deps.dev (T-18) but are not verified by
    # GHIMONEY and must be rejected explicitly, not silently accepted.
    with pytest.raises(DepsDevIngestionError):
        validate_ecosystem(ecosystem)


@pytest.mark.parametrize("name,version", [("", "1.0.0"), ("pkg", ""), ("has space", "1.0.0")])
def test_invalid_package_or_version_is_rejected(name, version):
    with pytest.raises(DepsDevIngestionError):
        validate_package(name, version)
