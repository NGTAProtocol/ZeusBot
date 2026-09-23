"""Command line interface: `ghimoney analyze owner/repository`."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ghimoney.engine import analyze
from ghimoney.evidence import parse_ts, project_identity
from ghimoney.ingestion import GitHubIngestor, IngestionError, validate_target
from ghimoney.methodology import load_methodology
from ghimoney.report import write_reports
from ghimoney.snapshot import Snapshot, SnapshotStore

DEFAULT_DB = Path(".ghimoney") / "snapshots.db"


def _resolve_snapshot(args, store: SnapshotStore, methodology) -> Snapshot:
    if args.snapshot_file:
        return Snapshot.load(args.snapshot_file)
    if args.snapshot:
        snap = store.get(args.snapshot)
        if snap is None:
            raise IngestionError(f"snapshot {args.snapshot} not found in {args.db}")
        return snap
    cached = store.latest(args.target)
    if cached is not None:
        age = datetime.now(timezone.utc) - parse_ts(cached.as_of)
        if args.offline or age <= timedelta(hours=args.max_age_hours):
            print(f"using cached snapshot {cached.snapshot_id} (as of {cached.as_of})",
                  file=sys.stderr)
            return cached
    if args.offline:
        raise IngestionError(f"no cached snapshot for {args.target} and --offline was given")
    print(f"fetching {args.target} from the GitHub API", file=sys.stderr)
    snap = GitHubIngestor(methodology).fetch(args.target)
    store.save(snap)
    return snap


def cmd_analyze(args) -> int:
    validate_target(args.target)
    methodology = load_methodology(args.config)
    store = SnapshotStore(args.db)
    try:
        snap = _resolve_snapshot(args, store, methodology)
        if snap.target.lower() != args.target.lower():
            raise IngestionError(f"snapshot {snap.snapshot_id} is for {snap.target}, "
                                 f"not {args.target}")
        identity = project_identity(snap)
        store.record_name("github", identity.forge_repo_id, identity.full_name, snap.as_of)
        report = analyze(snap, methodology)
    finally:
        store.close()
    out_dir = Path(args.out) / identity.full_name.replace("/", "__") / snap.snapshot_id
    json_path, md_path = write_reports(report, out_dir)
    impact = report["impact"]
    score = f"{impact['score']:.1f}" if impact["score"] is not None else impact["status"]
    print(f"Impact: {score} | Coverage: {report['coverage']['value']:.0%} | "
          f"Risk: {report['risk']['level']}")
    print(f"wrote {json_path}\nwrote {md_path}")
    return 0


def cmd_export_snapshot(args) -> int:
    store = SnapshotStore(args.db)
    try:
        snap = store.get(args.snapshot_id)
    finally:
        store.close()
    if snap is None:
        raise IngestionError(f"snapshot {args.snapshot_id} not found in {args.db}")
    snap.dump(args.path)
    print(f"wrote {args.path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ghimoney", description="GHIMONEY Impact Engine")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="snapshot store (SQLite)")
    sub = parser.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="analyze a GitHub repository")
    a.add_argument("target", help="owner/repository")
    a.add_argument("--config", help="methodology config (default: config/scoring.yaml)")
    a.add_argument("--out", default="reports", help="output directory")
    a.add_argument("--max-age-hours", type=float, default=24.0,
                   help="reuse a cached snapshot younger than this (default 24)")
    a.add_argument("--offline", action="store_true", help="never call the API")
    a.add_argument("--snapshot", help="re-analyze a stored snapshot id")
    a.add_argument("--snapshot-file", help="analyze a snapshot JSON file")
    a.set_defaults(func=cmd_analyze)

    e = sub.add_parser("export-snapshot", help="export a stored snapshot to JSON")
    e.add_argument("snapshot_id")
    e.add_argument("path")
    e.set_defaults(func=cmd_export_snapshot)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except IngestionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
