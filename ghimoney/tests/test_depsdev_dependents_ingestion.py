"""deps.dev GetDependents (v3alpha) ingestion against a mocked transport
(T-20). No real network use."""

from __future__ import annotations

import httpx

from ghimoney.depsdev_dependents_ingestion import DependentsIngestor

CALLS: list[str] = []


def handler(request: httpx.Request) -> httpx.Response:
    CALLS.append(request.url.raw_path.decode())
    path = request.url.path
    if path == "/v3alpha/systems/npm/packages/lodash/versions/4.17.21:dependents":
        return httpx.Response(200, json={"dependentCount": 22623, "directDependentCount": 7092,
                                         "indirectDependentCount": 16154})
    if path == "/v3alpha/systems/maven/packages/com.google.guava:guava/versions/32.1.3-jre:dependents":
        return httpx.Response(200, json={"dependentCount": 9397})
    if path == "/v3alpha/systems/npm/packages/nonexistent/versions/1.0.0:dependents":
        return httpx.Response(404, text="dependents not found")
    return httpx.Response(500, text=f"unexpected path in test: {path!r}")


def mock_ingestor() -> DependentsIngestor:
    CALLS.clear()
    client = httpx.Client(base_url="https://api.deps.dev", transport=httpx.MockTransport(handler))
    return DependentsIngestor(client)


def test_uses_v3alpha_not_v3():
    mock_ingestor().fetch("npm", "lodash", "4.17.21")
    assert any(c.startswith("/v3alpha/") for c in CALLS)
    assert not any(c.startswith("/v3/") for c in CALLS)


def test_supported_ecosystem_calls_dependents_endpoint():
    snap = mock_ingestor().fetch("npm", "lodash", "4.17.21")
    assert snap.get("dependents") is not None
    assert snap.get("dependents").status == 200
    assert snap.get("dependents").body["dependentCount"] == 22623


def test_go_makes_no_network_call():
    # D-12/T-20A: Go's gap is structural and ecosystem-wide; no call is
    # attempted, matching the economy already used in T-19 for Go's
    # :dependencies.
    snap = mock_ingestor().fetch("go", "github.com/pkg/errors", "v0.9.1")
    assert snap.get("dependents") is None
    assert len(CALLS) == 0


def test_maven_group_artifact_is_percent_encoded():
    mock_ingestor().fetch("maven", "com.google.guava:guava", "32.1.3-jre")
    assert any("com.google.guava%3Aguava" in c for c in CALLS)


def test_nonexistent_package_returns_404_snapshot():
    snap = mock_ingestor().fetch("npm", "nonexistent", "1.0.0")
    assert snap.get("dependents").status == 404


def test_fetch_is_reproducible():
    from dataclasses import replace
    a = mock_ingestor().fetch("npm", "lodash", "4.17.21")
    b = mock_ingestor().fetch("npm", "lodash", "4.17.21")
    b2 = replace(b, as_of=a.as_of)
    assert a.snapshot_hash == b2.snapshot_hash
