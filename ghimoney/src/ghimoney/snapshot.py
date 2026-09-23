"""Source snapshots: the frozen raw API responses an analysis is computed from.

The snapshot store doubles as the API cache (Directive §43). Scoring only ever
reads from a snapshot, never from the network, which is what makes
"same snapshot + same methodology -> same result" hold (Directive §45).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ghimoney.canonical import canonical_json, sha256_json

SNAPSHOT_FORMAT = "ghimoney-snapshot/1"


@dataclass(frozen=True)
class Response:
    endpoint: str
    status: int
    body: Any
    pages: int = 1
    truncated: bool = False

    @property
    def body_hash(self) -> str:
        return sha256_json(self.body)

    def to_dict(self) -> dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "status": self.status,
            "body": self.body,
            "pages": self.pages,
            "truncated": self.truncated,
        }


@dataclass(frozen=True)
class Snapshot:
    target: str
    source: str
    as_of: str
    api_version: str
    responses: dict[str, Response] = field(default_factory=dict)
    synthetic: bool = False

    def content(self) -> dict[str, Any]:
        return {
            "format": SNAPSHOT_FORMAT,
            "target": self.target,
            "source": self.source,
            "as_of": self.as_of,
            "api_version": self.api_version,
            "synthetic": self.synthetic,
            "responses": {k: r.to_dict() for k, r in self.responses.items()},
        }

    @property
    def snapshot_hash(self) -> str:
        return sha256_json(self.content())

    @property
    def snapshot_id(self) -> str:
        return self.snapshot_hash[:16]

    def get(self, key: str) -> Response | None:
        return self.responses.get(key)

    @classmethod
    def from_content(cls, data: dict[str, Any]) -> "Snapshot":
        if data.get("format") != SNAPSHOT_FORMAT:
            raise ValueError(f"unsupported snapshot format: {data.get('format')!r}")
        return cls(
            target=data["target"],
            source=data["source"],
            as_of=data["as_of"],
            api_version=data["api_version"],
            synthetic=bool(data.get("synthetic", False)),
            responses={k: Response(**v) for k, v in data["responses"].items()},
        )

    def dump(self, path: Path | str) -> None:
        Path(path).write_text(canonical_json(self.content(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str) -> "Snapshot":
        return cls.from_content(json.loads(Path(path).read_text(encoding="utf-8")))


_SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id   TEXT PRIMARY KEY,
    snapshot_hash TEXT NOT NULL,
    target        TEXT NOT NULL,
    as_of         TEXT NOT NULL,
    content       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS snapshots_target ON snapshots (target, as_of);
CREATE TABLE IF NOT EXISTS name_observations (
    forge          TEXT NOT NULL,
    forge_repo_id  INTEGER NOT NULL,
    full_name      TEXT NOT NULL,
    first_seen     TEXT NOT NULL,
    last_seen      TEXT NOT NULL,
    PRIMARY KEY (forge, forge_repo_id, full_name)
);
"""


class SnapshotStore:
    def __init__(self, path: Path | str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.executescript(_SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def save(self, snap: Snapshot) -> str:
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO snapshots VALUES (?, ?, ?, ?, ?)",
                (snap.snapshot_id, snap.snapshot_hash, snap.target.lower(), snap.as_of,
                 canonical_json(snap.content())),
            )
        return snap.snapshot_id

    def get(self, snapshot_id: str) -> Snapshot | None:
        row = self.conn.execute(
            "SELECT content, snapshot_hash FROM snapshots WHERE snapshot_id = ?", (snapshot_id,)
        ).fetchone()
        if row is None:
            return None
        snap = Snapshot.from_content(json.loads(row[0]))
        if snap.snapshot_hash != row[1]:
            raise ValueError(f"snapshot {snapshot_id} failed integrity check")
        return snap

    def latest(self, target: str) -> Snapshot | None:
        row = self.conn.execute(
            "SELECT snapshot_id FROM snapshots WHERE target = ? ORDER BY as_of DESC LIMIT 1",
            (target.lower(),),
        ).fetchone()
        return self.get(row[0]) if row else None

    def record_name(self, forge: str, repo_id: int, full_name: str, seen: str) -> None:
        """Keep a history of names per stable forge id (renames / transfers, Directive §5)."""
        with self.conn:
            self.conn.execute(
                """INSERT INTO name_observations VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT (forge, forge_repo_id, full_name) DO UPDATE SET
                     first_seen = min(first_seen, excluded.first_seen),
                     last_seen = max(last_seen, excluded.last_seen)""",
                (forge, repo_id, full_name, seen, seen),
            )

    def name_history(self, forge: str, repo_id: int) -> list[tuple[str, str, str]]:
        return self.conn.execute(
            "SELECT full_name, first_seen, last_seen FROM name_observations "
            "WHERE forge = ? AND forge_repo_id = ? ORDER BY first_seen",
            (forge, repo_id),
        ).fetchall()
