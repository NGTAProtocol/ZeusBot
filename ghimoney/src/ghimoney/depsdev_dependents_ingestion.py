"""deps.dev GetDependents (v3alpha) ingestion into a Snapshot (T-20, D-12).

This is the source for the Impact Engine's "dependency" dimension (D-12:
dependents, i.e. how much the ecosystem depends on the project). It is
deliberately separate from depsdev_ingestion.py (T-19's outgoing-dependency
evidence), which must not and does not feed this dimension.

Explicitly EXPERIMENTAL: `GetDependents` exists only in deps.dev's v3alpha
API, not the stable v3 (verified in T-20A: the same request against v3
returns HTTP 404 "version not found", while v3alpha returns HTTP 200 with
real data). v3alpha carries no stability guarantee or deprecation policy
(per the official README, read in T-18).

Ecosystem coverage (T-20A, empirical): npm, pypi, maven and cargo returned
real dependent counts. Go returned HTTP 404 "dependents not found" on two
different, real, well-known packages -- the same structural gap already
found for the outgoing dependency graph in T-19A. No call is attempted for
Go: the gap is ecosystem-wide, not per-package, so a per-call check would
only waste a request without adding information (same economy already
applied in T-19 for Go's :dependencies).
"""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote

from ghimoney.depsdev_ingestion import default_client, validate_ecosystem, validate_package
from ghimoney.snapshot import Response, Snapshot

API_VERSION = "v3alpha"
SOURCE = "deps-dev-api-v3alpha-dependents"

# Ecosystems with dependents data verified empirically in T-20A.
DEPENDENTS_ECOSYSTEMS = frozenset({"npm", "pypi", "maven", "cargo"})


class DependentsIngestionError(RuntimeError):
    pass


def _get(client, path: str) -> Response:
    resp = client.get(path)
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    return Response(endpoint=path, status=resp.status_code, body=body)


class DependentsIngestor:
    def __init__(self, client=None):
        self.client = client or default_client()

    def fetch(self, ecosystem: str, name: str, version: str,
             as_of: datetime | None = None) -> Snapshot:
        validate_ecosystem(ecosystem)
        validate_package(name, version)
        as_of = (as_of or datetime.now(timezone.utc)).replace(microsecond=0)
        as_of_iso = as_of.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        responses: dict[str, Response] = {}
        if ecosystem in DEPENDENTS_ECOSYSTEMS:
            encoded_name = quote(name, safe="")
            encoded_version = quote(version, safe="")
            path = (f"/v3alpha/systems/{ecosystem}/packages/{encoded_name}"
                    f"/versions/{encoded_version}:dependents")
            responses["dependents"] = _get(self.client, path)

        target = f"{ecosystem}:{name}@{version}"
        return Snapshot(target=target, source=SOURCE, as_of=as_of_iso,
                        api_version=API_VERSION, responses=responses)
