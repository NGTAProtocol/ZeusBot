#!/usr/bin/env python3
"""External GitHub snapshot collector for T-22.

Thin CLI wrapper around the already-verified `GitHubIngestor` and
`Snapshot` machinery (src/ghimoney/ingestion.py, src/ghimoney/snapshot.py).
It performs no HTTP, pagination, error-handling or normalization logic of
its own: it only calls GitHubIngestor.fetch() and writes the resulting
Snapshot with Snapshot.dump(), which already produces the exact
`ghimoney-snapshot/1` format (real endpoint/status/body/pages/truncated,
as_of, api_version, synthetic=false).

GITHUB_TOKEN is read from the environment only (never a CLI flag), via
ghimoney.ingestion.default_client(), which already does this.

Usage:
    python tools/collect_github_snapshot.py owner/repo --out snapshots/owner_repo.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ghimoney.ingestion import GitHubIngestor, IngestionError, RateLimitError, validate_target
from ghimoney.methodology import load_methodology


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="owner/repo")
    parser.add_argument("--out", required=True, help="output snapshot JSON path")
    parser.add_argument("--config", help="methodology config (default: config/scoring.yaml)")
    args = parser.parse_args(argv)

    try:
        validate_target(args.target)
        methodology = load_methodology(args.config)
        snapshot = GitHubIngestor(methodology).fetch(args.target)
    except (IngestionError, RateLimitError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot.dump(out_path)
    print(f"wrote snapshot {snapshot.snapshot_id} for {snapshot.target} to {out_path}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
