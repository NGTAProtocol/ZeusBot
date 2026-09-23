"""Loader for the real deps.dev fixtures captured in T-19A (fixtures/depsdev/)."""

from __future__ import annotations

import json
from pathlib import Path

from ghimoney.snapshot import Response, Snapshot

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "depsdev"
AS_OF = "2026-09-23T12:00:00Z"


def load_fixture(name: str) -> dict:
    """Returns {"status": int, "body": ...}, loaded from a real T-19A capture."""
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def response_from_fixture(name: str) -> Response:
    fx = load_fixture(name)
    return Response(endpoint=f"fixture:{name}", status=fx["status"], body=fx["body"])


def make_depsdev_snapshot(ecosystem: str, pkg_name: str, version: str,
                          **keyed_fixtures: str) -> Snapshot:
    """Builds a Snapshot exactly as depsdev_ingestion.DepsDevIngestor.fetch()
    would, from real fixture files rather than the network."""
    responses = {key: response_from_fixture(fixture) for key, fixture in keyed_fixtures.items()}
    return Snapshot(target=f"{ecosystem}:{pkg_name}@{version}", source="deps-dev-api-v3",
                    as_of=AS_OF, api_version="v3", responses=responses)
