"""deps.dev API v3 ingestion into a Snapshot (T-19, D-03 v2).

Scope and constraints, per DECISIONS.md D-03 (v2), docs/DEPS_DEV_EVALUATION.md
and docs/DEPS_DEV_EMPIRICAL_VERIFICATION.md:

- Only the ecosystems GHIMONEY targets are accepted: npm, pypi, maven, go,
  cargo. deps.dev also serves rubygems/nuget; GHIMONEY has not verified those
  and rejects them explicitly rather than guessing (D-03 condition 1).
- The resolved dependency graph (`GetDependencies`) is fetched only for the
  ecosystems T-19A verified to support it: npm, pypi, maven, cargo. Go does
  not have this endpoint -- verified empirically in T-19A (HTTP 404
  "dependencies not found" for a real, widely used package). For Go, the
  declared requirements (`GetRequirements`) are fetched instead: the only
  shape T-19A empirically verified for Go.
- A single attempt per endpoint, no retries: no numeric rate limit was ever
  confirmed (D-03 condition 5), so nothing here is built to depend on one.
- This module only produces a Snapshot. It never computes an Impact Score
  and is not called from ghimoney.engine.analyze(): see depsdev_evidence.py
  and DECISIONS.md.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

from ghimoney.snapshot import Response, Snapshot

API_ROOT = "https://api.deps.dev"
API_VERSION = "v3"
SOURCE = "deps-dev-api-v3"

# Ecosystems GHIMONEY targets (Directive requirement, scoped by T-18/T-19A).
ECOSYSTEMS = frozenset({"npm", "pypi", "maven", "go", "cargo"})

# Ecosystems with an empirically verified resolved dependency graph
# (T-19A T4/T7/T9/T14: HTTP 200 with a populated graph). Go is deliberately
# excluded: T-19A T12 confirmed GetDependencies returns HTTP 404
# "dependencies not found" for Go. Never treat that as "0 dependencies".
RESOLVED_GRAPH_ECOSYSTEMS = frozenset({"npm", "pypi", "maven", "cargo"})

_TOKEN_RE = re.compile(r"^\S+$")


class DepsDevIngestionError(RuntimeError):
    pass


def validate_ecosystem(ecosystem: str) -> str:
    if ecosystem not in ECOSYSTEMS:
        raise DepsDevIngestionError(
            f"unsupported ecosystem {ecosystem!r}: GHIMONEY only targets "
            f"{sorted(ECOSYSTEMS)} (D-03 condition 1). deps.dev may serve others, "
            "but they have not been verified in T-18/T-19A and are rejected "
            "rather than guessed at."
        )
    return ecosystem


def validate_package(name: str, version: str) -> tuple[str, str]:
    if not name or not _TOKEN_RE.match(name):
        raise DepsDevIngestionError(f"invalid package name: {name!r}")
    if not version or not _TOKEN_RE.match(version):
        raise DepsDevIngestionError(f"invalid version: {version!r}")
    return name, version


def default_client() -> httpx.Client:
    # T-18/T-19A found no authentication requirement documented or observed
    # for deps.dev v3 read endpoints; none is sent here.
    return httpx.Client(
        base_url=API_ROOT,
        headers={"Accept": "application/json", "User-Agent": "ghimoney-impact-engine"},
        timeout=30.0,
    )


def _get(client: httpx.Client, path: str) -> Response:
    resp = client.get(path)
    try:
        body = resp.json()
    except ValueError:
        # T-19A observed plain-text error bodies ("package not found",
        # "dependencies not found"), not JSON, on 404.
        body = resp.text
    return Response(endpoint=path, status=resp.status_code, body=body)


class DepsDevIngestor:
    """Fetches the minimal, empirically verified endpoint set for one
    (ecosystem, package, version): package existence, then either the
    resolved dependency graph or the declared requirements, depending on
    what T-19A verified for that ecosystem."""

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or default_client()

    def fetch(self, ecosystem: str, name: str, version: str,
             as_of: datetime | None = None) -> Snapshot:
        validate_ecosystem(ecosystem)
        validate_package(name, version)
        as_of = (as_of or datetime.now(timezone.utc)).replace(microsecond=0)
        as_of_iso = as_of.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        encoded_name = quote(name, safe="")
        responses: dict[str, Response] = {
            "package": _get(self.client, f"/v3/systems/{ecosystem}/packages/{encoded_name}"),
        }

        if responses["package"].status == 200:
            encoded_version = quote(version, safe="")
            base = (f"/v3/systems/{ecosystem}/packages/{encoded_name}"
                    f"/versions/{encoded_version}")
            if ecosystem in RESOLVED_GRAPH_ECOSYSTEMS:
                responses["dependencies"] = _get(self.client, f"{base}:dependencies")
            else:
                responses["requirements"] = _get(self.client, f"{base}:requirements")

        target = f"{ecosystem}:{name}@{version}"
        return Snapshot(target=target, source=SOURCE, as_of=as_of_iso,
                        api_version=API_VERSION, responses=responses)
