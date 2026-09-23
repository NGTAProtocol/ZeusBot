"""Determinism (§45), golden and regression tests (§47), snapshot integrity."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from conftest import FIXTURES, make_snapshot
from ghimoney.canonical import sha256_json
from ghimoney.engine import analyze
from ghimoney.report import render_json, render_markdown
from ghimoney.snapshot import Snapshot, SnapshotStore

GOLDEN_SNAPSHOT = FIXTURES / "synthetic_library.snapshot.json"
GOLDEN_REPORT = FIXTURES / "golden" / "synthetic_library.report.json"


def test_run_a_equals_run_b(snapshot, methodology):
    a, b = analyze(snapshot, methodology), analyze(snapshot, methodology)
    assert render_json(a) == render_json(b)
    assert render_markdown(a) == render_markdown(b)


def test_determinism_across_processes(tmp_path):
    # Separate interpreters with different hash seeds must agree byte for byte.
    code = ("import sys; from ghimoney.engine import analyze; "
            "from ghimoney.methodology import load_methodology; "
            "from ghimoney.snapshot import Snapshot; from ghimoney.report import render_json; "
            f"sys.stdout.write(render_json(analyze(Snapshot.load({str(GOLDEN_SNAPSHOT)!r}), "
            "load_methodology())))")
    outputs = set()
    for seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        outputs.add(subprocess.run([sys.executable, "-c", code], env=env, check=True,
                                   capture_output=True, text=True).stdout)
    assert len(outputs) == 1


def test_report_hash_covers_content(snapshot, methodology):
    report = analyze(snapshot, methodology)
    body = {k: v for k, v in report.items() if k != "report_hash"}
    assert report["report_hash"] == sha256_json(body)


def test_snapshot_roundtrip(tmp_path, snapshot):
    path = tmp_path / "snap.json"
    snapshot.dump(path)
    assert Snapshot.load(path).snapshot_hash == snapshot.snapshot_hash


def test_store_roundtrip_and_tamper_detection(tmp_path, snapshot):
    store = SnapshotStore(tmp_path / "db.sqlite")
    sid = store.save(snapshot)
    assert store.get(sid).snapshot_hash == snapshot.snapshot_hash
    assert store.latest("SYNTHETIC/Library").snapshot_id == sid
    store.conn.execute("UPDATE snapshots SET content = replace(content, '850', '851')")
    with pytest.raises(ValueError, match="integrity"):
        store.get(sid)
    store.close()


def test_name_history_tracks_renames(tmp_path):
    store = SnapshotStore(tmp_path / "db.sqlite")
    store.record_name("github", 1, "old/name", "2026-01-01T00:00:00Z")
    store.record_name("github", 1, "new/name", "2026-02-01T00:00:00Z")
    store.record_name("github", 1, "old/name", "2025-12-01T00:00:00Z")
    assert store.name_history("github", 1) == [
        ("old/name", "2025-12-01T00:00:00Z", "2026-01-01T00:00:00Z"),
        ("new/name", "2026-02-01T00:00:00Z", "2026-02-01T00:00:00Z"),
    ]
    store.close()


def test_golden_fixture_matches_builder():
    # The committed fixture is the synthetic builder's output, frozen.
    assert Snapshot.load(GOLDEN_SNAPSHOT).snapshot_hash == make_snapshot().snapshot_hash


def test_golden_report(methodology):
    """Regression: a report may only change together with a declared methodology change."""
    expected = json.loads(GOLDEN_REPORT.read_text())
    actual = json.loads(render_json(analyze(Snapshot.load(GOLDEN_SNAPSHOT), methodology)))
    if actual["methodology"]["config_hash"] != expected["methodology"]["config_hash"]:
        assert (actual["methodology"]["methodology_version"]
                != expected["methodology"]["methodology_version"]), (
            "config changed without a new methodology_version (Directive §44)")
        pytest.skip("methodology changed: regenerate the golden report")
    assert actual == expected
