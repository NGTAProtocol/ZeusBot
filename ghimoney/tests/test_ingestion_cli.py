"""Ingestion against a mocked GitHub API, and the CLI end to end (offline)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx
import pytest

from conftest import FIXTURES
from ghimoney.cli import main
from ghimoney.ingestion import GitHubIngestor, IngestionError, RateLimitError, validate_target

AS_OF = datetime(2026, 9, 1, tzinfo=timezone.utc)


def mock_github(handler):
    return httpx.Client(base_url="https://api.github.com", transport=httpx.MockTransport(handler))


def ok_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/repos/o/r":
        return httpx.Response(200, json={"id": 7, "full_name": "o/r", "fork": False,
                                         "created_at": "2020-01-01T00:00:00Z"})
    if path == "/repos/o/r/contributors":
        page = int(request.url.params.get("page", "1"))
        headers = {}
        if page < 9:  # more pages exist than the limit allows
            headers["Link"] = f'<https://api.github.com/repos/o/r/contributors?per_page=100&page={page + 1}>; rel="next"'
        return httpx.Response(200, json=[{"login": f"u{page}-{i}"} for i in range(100)],
                              headers=headers)
    if path.startswith("/repos/o/r/contents/"):
        return httpx.Response(404, json={"message": "Not Found"})
    if path == "/repos/o/r/community/profile":
        return httpx.Response(200, json={"files": {}})
    if path == "/repos/o/r/actions/workflows":
        return httpx.Response(200, json={"total_count": 0, "workflows": []})
    return httpx.Response(200, json=[])


def test_fetch_builds_snapshot_with_pagination_limits(methodology):
    snap = GitHubIngestor(methodology, mock_github(ok_handler)).fetch("o/r", as_of=AS_OF)
    contributors = snap.get("contributors")
    assert contributors.pages == methodology.ingestion.max_pages_contributors
    assert contributors.truncated is True
    assert len(contributors.body) == 100 * methodology.ingestion.max_pages_contributors
    assert snap.get("security_policy:SECURITY.md").status == 404
    assert snap.as_of == "2026-09-01T00:00:00Z"
    assert "since=2025-09-01T00:00:00Z" in snap.get("commits_window").endpoint


def test_fetch_is_reproducible_for_same_api_state(methodology):
    a = GitHubIngestor(methodology, mock_github(ok_handler)).fetch("o/r", as_of=AS_OF)
    b = GitHubIngestor(methodology, mock_github(ok_handler)).fetch("o/r", as_of=AS_OF)
    assert a.snapshot_hash == b.snapshot_hash


def test_rate_limit_is_reported(methodology):
    def handler(request):
        return httpx.Response(403, json={"message": "rate limit"},
                              headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1"})
    with pytest.raises(RateLimitError):
        GitHubIngestor(methodology, mock_github(handler)).fetch("o/r", as_of=AS_OF)


def test_unreadable_repository_fails(methodology):
    with pytest.raises(IngestionError, match="not readable"):
        GitHubIngestor(methodology, mock_github(lambda r: httpx.Response(404, json={}))).fetch(
            "o/r", as_of=AS_OF)


@pytest.mark.parametrize("bad", ["o", "o/r/x", "../etc", "o/..", "o r/x", "-o/r", ""])
def test_invalid_targets_are_rejected(bad):
    with pytest.raises(IngestionError):
        validate_target(bad)


def test_cli_analyze_offline_snapshot_file(tmp_path, capsys):
    rc = main(["--db", str(tmp_path / "db.sqlite"), "analyze", "synthetic/library",
               "--snapshot-file", str(FIXTURES / "synthetic_library.snapshot.json"),
               "--out", str(tmp_path / "reports")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "INSUFFICIENT_EVIDENCE" in out
    report_json = next((tmp_path / "reports").rglob("report.json"))
    report = json.loads(report_json.read_text())
    assert report["source"]["synthetic"] is True
    assert "SYNTHETIC DATA" in report_json.with_name("report.md").read_text()


def test_cli_rejects_snapshot_of_another_repository(tmp_path, capsys):
    rc = main(["--db", str(tmp_path / "db.sqlite"), "analyze", "other/repo",
               "--snapshot-file", str(FIXTURES / "synthetic_library.snapshot.json"),
               "--out", str(tmp_path / "reports")])
    assert rc == 2
    assert "not other/repo" in capsys.readouterr().err


def test_cli_offline_without_cache_fails(tmp_path, capsys):
    rc = main(["--db", str(tmp_path / "db.sqlite"), "analyze", "o/r", "--offline"])
    assert rc == 2
    assert "no cached snapshot" in capsys.readouterr().err
