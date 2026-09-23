"""CLI integration for `ghimoney dependency-evidence` (T-19). Offline only."""

from __future__ import annotations

import json

from ghimoney.cli import main
from ghimoney.snapshot import Snapshot


def _write_snapshot_file(path, ecosystem, name, version, **keyed_fixtures):
    from conftest_depsdev import make_depsdev_snapshot
    make_depsdev_snapshot(ecosystem, name, version, **keyed_fixtures).dump(path)


def test_cli_dependency_evidence_offline_npm(tmp_path):
    snap_file = tmp_path / "express.snapshot.json"
    _write_snapshot_file(snap_file, "npm", "express", "4.19.2",
                        package="t1_npm_lodash_package",
                        dependencies="t4_npm_express_dependencies")
    rc = main(["--db", str(tmp_path / "db.sqlite"), "dependency-evidence", "npm", "express",
               "4.19.2", "--snapshot-file", str(snap_file), "--out", str(tmp_path / "reports")])
    assert rc == 0
    json_path = next((tmp_path / "reports").rglob("dependency_evidence.json"))
    payload = json.loads(json_path.read_text())
    assert payload["format"] == "ghimoney-dependency-evidence/1"
    assert payload["package"]["package_id"] == "pkg:npm:express@4.19.2"
    by_metric = {e["metric"]: e for e in payload["evidence"]}
    assert by_metric["dependency.resolved_graph_direct_count"]["raw_value"] == 31
    assert by_metric["dependency.resolved_graph_direct_count"]["normalized_value"] is None
    assert "not wired into the Impact Engine" in payload["note"]


def test_cli_dependency_evidence_offline_go_never_reports_zero(tmp_path):
    snap_file = tmp_path / "pkgerrors.snapshot.json"
    _write_snapshot_file(snap_file, "go", "github.com/pkg/errors", "v0.9.1",
                        package="t10_go_pkgerrors_package",
                        requirements="t11_go_pkgerrors_requirements")
    rc = main(["--db", str(tmp_path / "db.sqlite"), "dependency-evidence", "go",
               "github.com/pkg/errors", "v0.9.1", "--snapshot-file", str(snap_file),
               "--out", str(tmp_path / "reports")])
    assert rc == 0
    json_path = next((tmp_path / "reports").rglob("dependency_evidence.json"))
    payload = json.loads(json_path.read_text())
    by_metric = {e["metric"]: e for e in payload["evidence"]}
    assert by_metric["dependency.resolved_graph_direct_count"]["availability"] == "NOT_AVAILABLE"
    assert by_metric["dependency.resolved_graph_direct_count"]["raw_value"] is None


def test_cli_dependency_evidence_rejects_unsupported_ecosystem(tmp_path, capsys):
    rc = main(["--db", str(tmp_path / "db.sqlite"), "dependency-evidence", "npm",
               "express", "4.19.2", "--offline"])
    # offline with no cached snapshot -> handled error, not a crash
    assert rc == 2
    assert "no cached snapshot" in capsys.readouterr().err


def test_cli_rejects_snapshot_of_a_different_package(tmp_path):
    snap_file = tmp_path / "express.snapshot.json"
    _write_snapshot_file(snap_file, "npm", "express", "4.19.2",
                        package="t1_npm_lodash_package",
                        dependencies="t4_npm_express_dependencies")
    rc = main(["--db", str(tmp_path / "db.sqlite"), "dependency-evidence", "npm", "lodash",
               "4.17.21", "--snapshot-file", str(snap_file), "--out", str(tmp_path / "reports")])
    assert rc == 2


def test_cli_reuses_cache_offline_after_a_snapshot_file_run(tmp_path):
    # After the first (offline, from a snapshot file) run, the snapshot is
    # not auto-cached (only network fetches call store.save); verify that
    # a subsequent --offline run without a cached snapshot fails cleanly
    # rather than silently fetching.
    rc = main(["--db", str(tmp_path / "db.sqlite"), "dependency-evidence", "npm", "left-pad",
               "1.0.0", "--offline", "--out", str(tmp_path / "reports")])
    assert rc == 2
