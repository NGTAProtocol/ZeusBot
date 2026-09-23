"""Synthetic GitHub API snapshots for tests. All data here is SYNTHETIC."""

from __future__ import annotations

import copy
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from ghimoney.methodology import load_methodology
from ghimoney.snapshot import Response, Snapshot

AS_OF = datetime(2026, 9, 1, tzinfo=timezone.utc)
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def ts(days_ago: float) -> str:
    return (AS_OF - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def commit(days_ago: float, login: str | None, email: str = "dev@example.invalid") -> dict:
    return {
        "sha": hashlib.sha1(f"{days_ago}|{login}|{email}".encode()).hexdigest(),
        "author": {"login": login} if login else None,
        "commit": {
            "author": {"name": login or "anon", "email": email, "date": ts(days_ago)},
            "committer": {"name": login or "anon", "email": email, "date": ts(days_ago)},
        },
    }


def base_responses() -> dict[str, dict[str, Any]]:
    """A healthy, mid-sized synthetic library."""
    authors = [f"dev{i}" for i in range(8)]
    commits = [commit(d * 3 + 1, authors[d % len(authors)]) for d in range(120)]
    return {
        "repo": {"status": 200, "body": {
            "id": 424242, "node_id": "R_synthetic", "full_name": "synthetic/library",
            "fork": False, "archived": False, "stargazers_count": 850, "forks_count": 90,
            "subscribers_count": 30, "created_at": ts(1500)}},
        "latest_commit": {"status": 200, "body": commits[:1]},
        "commits_window": {"status": 200, "body": commits},
        "releases": {"status": 200, "body": [
            {"draft": False, "published_at": ts(d)} for d in (20, 80, 150, 260, 400)]},
        "contributors": {"status": 200, "body": [{"login": f"c{i}"} for i in range(25)]},
        "community_profile": {"status": 200, "body": {"files": {
            "readme": {}, "license": {}, "contributing": {}, "code_of_conduct": None,
            "issue_template": {}, "pull_request_template": None}}},
        "workflows": {"status": 200, "body": {"total_count": 3, "workflows": []}},
        "security_advisories": {"status": 200, "body": []},
        "security_policy:SECURITY.md": {"status": 200, "body": {"name": "SECURITY.md"}},
        "security_policy:.github/SECURITY.md": {"status": 404, "body": {"message": "Not Found"}},
        "security_policy:docs/SECURITY.md": {"status": 404, "body": {"message": "Not Found"}},
    }


def make_snapshot(overrides: dict[str, dict[str, Any] | None] | None = None,
                  repo_fields: dict[str, Any] | None = None) -> Snapshot:
    responses = base_responses()
    for key, value in (overrides or {}).items():
        if value is None:
            responses.pop(key, None)
        else:
            responses[key] = value
    if repo_fields:
        responses["repo"] = copy.deepcopy(responses["repo"])
        responses["repo"]["body"].update(repo_fields)
    return Snapshot(
        target=responses["repo"]["body"]["full_name"],
        source="github-rest-api",
        as_of=AS_OF.strftime("%Y-%m-%dT%H:%M:%SZ"),
        api_version="2022-11-28",
        synthetic=True,
        responses={k: Response(endpoint=f"/synthetic/{k}", status=v["status"], body=v["body"],
                               pages=v.get("pages", 1), truncated=v.get("truncated", False))
                   for k, v in responses.items()},
    )


@pytest.fixture
def methodology():
    return load_methodology()


@pytest.fixture
def snapshot():
    return make_snapshot()
