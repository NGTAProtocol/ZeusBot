"""Command line interface: `ghimoney analyze owner/repository`."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ghimoney.canonical import canonical_json
from ghimoney.depsdev_dependents_evidence import build_dependents_evidence
from ghimoney.depsdev_dependents_ingestion import DependentsIngestor
from ghimoney.depsdev_evidence import build_dependency_evidence, package_id
from ghimoney.depsdev_ingestion import (
    ECOSYSTEMS,
    DepsDevIngestionError,
    DepsDevIngestor,
    validate_ecosystem,
    validate_package,
)
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


def _parse_package_ref(ref: str) -> tuple[str, str, str]:
    """Parses "ecosystem:name@version" (e.g. "npm:@babel/core@7.20.0").
    Split on the first ":" then the LAST "@", since a scoped npm name
    itself starts with "@"."""
    if ":" not in ref or "@" not in ref.split(":", 1)[1]:
        raise DepsDevIngestionError(
            f"invalid package reference {ref!r}: expected ecosystem:name@version")
    ecosystem, rest = ref.split(":", 1)
    name, version = rest.rsplit("@", 1)
    return ecosystem, name, version


def _resolve_dependents_evidence(args, store: SnapshotStore, methodology):
    """T-20, D-12: the ONLY evidence allowed to feed the "dependency"
    dimension. Requires the caller to explicitly name the package
    (--dependents ecosystem:name@version): GHIMONEY does not correlate a
    GitHub project to a registry package automatically -- that mapping is
    not defined by any decision and is not guessed here."""
    ecosystem, name, version = _parse_package_ref(args.dependents)
    validate_ecosystem(ecosystem)
    validate_package(name, version)
    target = f"{ecosystem}:{name}@{version}"
    if args.dependents_snapshot_file:
        snap = Snapshot.load(args.dependents_snapshot_file)
    elif args.offline:
        snap = store.latest(target)
        if snap is None:
            raise DepsDevIngestionError(
                f"no cached dependents snapshot for {target} and --offline was given")
    else:
        print(f"fetching dependents for {target} from deps.dev "
              "(v3alpha, EXPERIMENTAL SOURCE)", file=sys.stderr)
        snap = DependentsIngestor().fetch(ecosystem, name, version)
        store.save(snap)
    if snap.target.lower() != target.lower():
        raise DepsDevIngestionError(
            f"dependents snapshot {snap.snapshot_id} is for {snap.target}, not {target}")
    return build_dependents_evidence(snap, ecosystem, name, version, methodology)


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
        extra_evidence = (_resolve_dependents_evidence(args, store, methodology)
                          if args.dependents else None)
        report = analyze(snap, methodology, extra_evidence=extra_evidence)
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


def cmd_dependency_evidence(args) -> int:
    """T-19: Dependency Evidence from deps.dev (outgoing dependencies).
    Standalone from `analyze`: per D-12, this never feeds the Impact
    Engine's "dependency" dimension, which measures dependents instead
    (see cmd_analyze's --dependents option, T-20)."""
    validate_ecosystem(args.ecosystem)
    validate_package(args.name, args.version)
    methodology = load_methodology(args.config)
    target = f"{args.ecosystem}:{args.name}@{args.version}"
    store = SnapshotStore(args.db)
    try:
        if args.snapshot_file:
            snap = Snapshot.load(args.snapshot_file)
        elif args.offline:
            snap = store.latest(target)
            if snap is None:
                raise DepsDevIngestionError(
                    f"no cached snapshot for {target} and --offline was given")
        else:
            print(f"fetching {target} from deps.dev", file=sys.stderr)
            snap = DepsDevIngestor().fetch(args.ecosystem, args.name, args.version)
            store.save(snap)
        if snap.target.lower() != target.lower():
            raise DepsDevIngestionError(
                f"snapshot {snap.snapshot_id} is for {snap.target}, not {target}")
        evidence = build_dependency_evidence(snap, args.ecosystem, args.name, args.version,
                                             methodology)
    finally:
        store.close()

    pkg_id = package_id(args.ecosystem, args.name, args.version)
    out_dir = Path(args.out) / pkg_id.replace("/", "__") / snap.snapshot_id
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": "ghimoney-dependency-evidence/1",
        "package": {"ecosystem": args.ecosystem, "name": args.name, "version": args.version,
                    "package_id": pkg_id},
        "source": {"snapshot_id": snap.snapshot_id, "snapshot_hash": snap.snapshot_hash,
                  "as_of": snap.as_of, "source": snap.source, "api_version": snap.api_version},
        "evidence": [e.model_dump(mode="json") for e in evidence],
        "note": "Outgoing Dependency Evidence only: not scored, does not feed the Impact "
                "Engine's 'dependency' dimension, which measures dependents instead (D-12).",
    }
    json_path = out_dir / "dependency_evidence.json"
    json_path.write_text(canonical_json(payload, indent=2) + "\n", encoding="utf-8")
    for e in evidence:
        value = f" = {e.raw_value!r}" if e.availability.value == "VERIFIED" else ""
        print(f"{e.metric}: {e.availability.value}{value}")
    print(f"wrote {json_path}")
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
    a.add_argument("--dependents", metavar="ECOSYSTEM:NAME@VERSION",
                   help="score the 'dependency' dimension from this package's dependents "
                        "(T-20, D-12; deps.dev GetDependents, v3alpha EXPERIMENTAL SOURCE). "
                        "GHIMONEY does not auto-detect a project's package: name it explicitly.")
    a.add_argument("--dependents-snapshot-file",
                   help="use a dependents snapshot JSON file instead of fetching")
    a.set_defaults(func=cmd_analyze)

    e = sub.add_parser("export-snapshot", help="export a stored snapshot to JSON")
    e.add_argument("snapshot_id")
    e.add_argument("path")
    e.set_defaults(func=cmd_export_snapshot)

    d = sub.add_parser("dependency-evidence",
                       help="fetch Dependency Evidence for a package from deps.dev (T-19)")
    d.add_argument("ecosystem", choices=sorted(ECOSYSTEMS))
    d.add_argument("name", help="package name")
    d.add_argument("version", help="package version")
    d.add_argument("--config", help="methodology config (default: config/scoring.yaml)")
    d.add_argument("--out", default="reports", help="output directory")
    d.add_argument("--offline", action="store_true", help="never call the API")
    d.add_argument("--snapshot-file", help="use a snapshot JSON file instead of fetching")
    d.set_defaults(func=cmd_dependency_evidence)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (IngestionError, DepsDevIngestionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
