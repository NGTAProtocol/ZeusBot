"""External GitHub snapshot collector (T-22 support tool). Offline only:
GitHubIngestor's HTTP client is monkeypatched with httpx.MockTransport, so
no test here depends on the network. Mirrors test_ingestion_cli.py's mock
pattern.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import httpx
import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
spec = importlib.util.spec_from_file_location(
    "collect_github_snapshot", TOOLS_DIR / "collect_github_snapshot.py")
collect_github_snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect_github_snapshot)

from ghimoney.cli import main as ghimoney_main
from ghimoney.snapshot import Snapshot, SNAPSHOT_FORMAT


def ok_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/repos/o/r":
        return httpx.Response(200, json={"id": 7, "full_name": "o/r", "fork": False,
                                         "created_at": "2020-01-01T00:00:00Z"})
    if path.startswith("/repos/o/r/contents/"):
        return httpx.Response(404, json={"message": "Not Found"})
    if path == "/repos/o/r/community/profile":
        return httpx.Response(200, json={"files": {}})
    if path == "/repos/o/r/actions/workflows":
        return httpx.Response(200, json={"total_count": 0, "workflows": []})
    return httpx.Response(200, json=[])


def mock_client(token=None):
    return httpx.Client(base_url="https://api.github.com",
                        transport=httpx.MockTransport(ok_handler))


def test_collector_writes_valid_ghimoney_snapshot(tmp_path, monkeypatch):
    monkeypatch.setattr("ghimoney.ingestion.default_client", mock_client)
    out = tmp_path / "o_r.snapshot.json"

    rc = collect_github_snapshot.main(["o/r", "--out", str(out)])
    assert rc == 0
    assert out.exists()

    payload = json.loads(out.read_text())
    assert payload["format"] == SNAPSHOT_FORMAT
    assert payload["target"] == "o/r"
    assert payload["source"] == "github-rest-api"
    assert payload["synthetic"] is False
    assert "as_of" in payload and "api_version" in payload
    repo_resp = payload["responses"]["repo"]
    assert repo_resp["endpoint"] == "/repos/o/r"
    assert repo_resp["status"] == 200
    assert repo_resp["body"]["full_name"] == "o/r"


def test_collector_output_is_deterministic(tmp_path, monkeypatch):
    monkeypatch.setattr("ghimoney.ingestion.default_client", mock_client)
    out_a = tmp_path / "a.json"
    out_b = tmp_path / "b.json"
    collect_github_snapshot.main(["o/r", "--out", str(out_a)])
    collect_github_snapshot.main(["o/r", "--out", str(out_b)])
    assert out_a.read_text() == out_b.read_text()


def test_collected_snapshot_is_accepted_by_ghimoney_analyze(tmp_path, monkeypatch):
    monkeypatch.setattr("ghimoney.ingestion.default_client", mock_client)
    snap_file = tmp_path / "o_r.snapshot.json"
    rc = collect_github_snapshot.main(["o/r", "--out", str(snap_file)])
    assert rc == 0

    # Verify the file round-trips through Snapshot.load() (integrity check).
    loaded = Snapshot.load(snap_file)
    assert loaded.target == "o/r"

    rc = ghimoney_main(["--db", str(tmp_path / "db.sqlite"), "analyze", "o/r",
                       "--snapshot-file", str(snap_file), "--out", str(tmp_path / "reports")])
    assert rc == 0
    report_json = next((tmp_path / "reports").rglob("report.json"))
    report = json.loads(report_json.read_text())
    assert report["source"]["synthetic"] is False


def test_collector_rejects_invalid_target(tmp_path, capsys):
    rc = collect_github_snapshot.main(["not-a-valid-target", "--out", str(tmp_path / "x.json")])
    assert rc == 2
    assert "error:" in capsys.readouterr().err


def test_collector_reports_unreadable_repository(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("ghimoney.ingestion.default_client",
                        lambda token=None: httpx.Client(
                            base_url="https://api.github.com",
                            transport=httpx.MockTransport(lambda r: httpx.Response(404, json={}))))
    rc = collect_github_snapshot.main(["o/r", "--out", str(tmp_path / "x.json")])
    assert rc == 2
    assert "not readable" in capsys.readouterr().err
