"""Turn a Snapshot into Evidence Records (Directive §8).

Scored metrics are listed in the methodology config. Signals (stars, forks,
age, ...) are recorded as evidence but never scored (Rule 2); the Risk Engine
reads them.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable

from ghimoney.methodology import Methodology
from ghimoney.models import Availability, EvidenceRecord, ProjectIdentity, Provenance
from ghimoney.normalization import normalize
from ghimoney.snapshot import Snapshot

COMMUNITY_FILES = ("readme", "license", "contributing", "code_of_conduct",
                   "issue_template", "pull_request_template")
EMPTY_REPO_STATUS = 409  # GitHub returns 409 on /commits for an empty repository


@dataclass(frozen=True)
class Observation:
    availability: Availability
    value: Any = None
    kind: str | None = None
    keys: tuple[str, ...] = ()
    note: str | None = None


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def project_identity(snap: Snapshot) -> ProjectIdentity:
    repo = snap.get("repo").body
    forge_repo_id = int(repo["id"])
    digest = hashlib.sha256(f"github-repo-id:{forge_repo_id}".encode()).hexdigest()
    return ProjectIdentity(
        project_id=f"ghp-{digest[:16]}",
        forge="github",
        forge_repo_id=forge_repo_id,
        forge_node_id=repo.get("node_id"),
        full_name=repo["full_name"],
        is_fork=repo.get("fork"),
        is_archived=repo.get("archived"),
    )


def _unavailable(key: str, snap: Snapshot) -> Observation:
    resp = snap.get(key)
    status = resp.status if resp else "missing"
    return Observation(Availability.NOT_AVAILABLE, keys=(key,),
                       note=f"source request {key!r} unavailable (HTTP {status})")


def _commits(snap: Snapshot) -> tuple[list[dict] | None, bool, int | None]:
    resp = snap.get("commits_window")
    if resp is None:
        return None, False, None
    if resp.status == EMPTY_REPO_STATUS:
        return [], False, resp.status
    if resp.status != 200 or not isinstance(resp.body, list):
        return None, False, resp.status
    return resp.body, resp.truncated, resp.status


def _author_key(commit: dict) -> str:
    author = commit.get("author") or {}
    if author.get("login"):
        return f"login:{author['login'].lower()}"
    email = ((commit.get("commit") or {}).get("author") or {}).get("email") or ""
    # Only a hash is kept in memory; emails never reach reports (Directive §36).
    return "email:" + hashlib.sha256(email.lower().encode()).hexdigest()


def _commit_date(commit: dict) -> datetime:
    return parse_ts(commit["commit"]["committer"]["date"])


# --------------------------------------------------------------------------
# Scored metrics
# --------------------------------------------------------------------------

def obs_commits_last_365d(snap: Snapshot, as_of: datetime) -> Observation:
    commits, truncated, status = _commits(snap)
    if commits is None:
        return _unavailable("commits_window", snap)
    note = "empty repository" if status == EMPTY_REPO_STATUS else None
    if truncated:
        note = "pagination limit reached: value is a lower bound"
    return Observation(Availability.VERIFIED, len(commits),
                       "lower_bound" if truncated else "direct_count", ("commits_window",), note)


def obs_days_since_last_commit(snap: Snapshot, as_of: datetime) -> Observation:
    resp = snap.get("latest_commit")
    if resp is not None and resp.status == EMPTY_REPO_STATUS:
        return Observation(Availability.NOT_APPLICABLE, keys=("latest_commit",),
                           note="empty repository: no commit exists")
    if resp is None or resp.status != 200 or not resp.body:
        return _unavailable("latest_commit", snap)
    days = max(0.0, (as_of - _commit_date(resp.body[0])).total_seconds() / 86400)
    return Observation(Availability.VERIFIED, round(days, 2), "derived", ("latest_commit",))


def obs_releases_last_365d(snap: Snapshot, as_of: datetime, window_days: int) -> Observation:
    resp = snap.get("releases")
    if resp is None or resp.status != 200 or not isinstance(resp.body, list):
        return _unavailable("releases", snap)
    published = [r for r in resp.body if not r.get("draft") and r.get("published_at")]
    if not published:
        return Observation(Availability.UNKNOWN, keys=("releases",),
                           note="no GitHub Releases: the project may release through tags or "
                                "package registries, so absence is not evidence of zero releases")
    since = as_of - timedelta(days=window_days)
    in_window = [r for r in published if since <= parse_ts(r["published_at"]) <= as_of]
    oldest = min(parse_ts(r["published_at"]) for r in published)
    lower_bound = resp.truncated and oldest >= since
    return Observation(Availability.VERIFIED, len(in_window),
                       "lower_bound" if lower_bound else "direct_count", ("releases",),
                       "pagination limit reached: value is a lower bound" if lower_bound else None)


def obs_community_profile_files(snap: Snapshot, as_of: datetime) -> Observation:
    resp = snap.get("community_profile")
    if resp is None or resp.status != 200 or not isinstance(resp.body, dict):
        return _unavailable("community_profile", snap)
    files = resp.body.get("files") or {}
    present = [f for f in COMMUNITY_FILES
               if files.get(f) is not None
               or (f == "code_of_conduct" and files.get("code_of_conduct_file") is not None)]
    return Observation(Availability.VERIFIED, round(len(present) / len(COMMUNITY_FILES), 4),
                       "derived", ("community_profile",),
                       "present: " + (", ".join(present) if present else "none"))


def obs_ci_workflows_present(snap: Snapshot, as_of: datetime) -> Observation:
    resp = snap.get("workflows")
    if resp is None or resp.status != 200 or not isinstance(resp.body, dict):
        return _unavailable("workflows", snap)
    if int(resp.body.get("total_count", 0)) > 0:
        return Observation(Availability.VERIFIED, True, "presence_check", ("workflows",))
    return Observation(Availability.UNKNOWN, keys=("workflows",),
                       note="no GitHub Actions workflows: CI may run on another service, "
                            "so absence is not evidence of no CI")


def obs_security_policy_present(snap: Snapshot, as_of: datetime, paths: list[str]) -> Observation:
    keys = tuple(f"security_policy:{p}" for p in paths)
    statuses = [snap.get(k).status if snap.get(k) else None for k in keys]
    if 200 in statuses:
        return Observation(Availability.VERIFIED, True, "presence_check", keys)
    if all(s == 404 for s in statuses):
        return Observation(Availability.VERIFIED, False, "absence_check", keys,
                           "no SECURITY.md in: " + ", ".join(paths))
    return Observation(Availability.NOT_AVAILABLE, keys=keys,
                       note=f"security policy lookup incomplete (HTTP {statuses})")


def obs_distinct_authors_last_365d(snap: Snapshot, as_of: datetime) -> Observation:
    commits, truncated, _ = _commits(snap)
    if commits is None:
        return _unavailable("commits_window", snap)
    return Observation(Availability.VERIFIED, len({_author_key(c) for c in commits}),
                       "lower_bound" if truncated else "direct_count", ("commits_window",),
                       "pagination limit reached: value is a lower bound" if truncated else None)


def obs_total_contributors(snap: Snapshot, as_of: datetime) -> Observation:
    resp = snap.get("contributors")
    if resp is not None and resp.status == 204:
        return Observation(Availability.VERIFIED, 0, "direct_count", ("contributors",),
                           "empty repository")
    if resp is None or resp.status != 200 or not isinstance(resp.body, list):
        return _unavailable("contributors", snap)
    return Observation(Availability.VERIFIED, len(resp.body),
                       "lower_bound" if resp.truncated else "direct_count", ("contributors",),
                       "pagination limit reached: value is a lower bound" if resp.truncated else None)


# --------------------------------------------------------------------------
# Signals: recorded, never scored
# --------------------------------------------------------------------------

def _repo_field(field: str) -> Callable[[Snapshot, datetime], Observation]:
    def extract(snap: Snapshot, as_of: datetime) -> Observation:
        value = snap.get("repo").body.get(field)
        if value is None:
            return _unavailable("repo", snap)
        return Observation(Availability.VERIFIED, value, "direct_count", ("repo",))
    return extract


def obs_repository_age_days(snap: Snapshot, as_of: datetime) -> Observation:
    created = snap.get("repo").body.get("created_at")
    if not created:
        return _unavailable("repo", snap)
    return Observation(Availability.VERIFIED,
                       round((as_of - parse_ts(created)).total_seconds() / 86400, 2),
                       "derived", ("repo",))


def obs_published_security_advisories(snap: Snapshot, as_of: datetime) -> Observation:
    resp = snap.get("security_advisories")
    if resp is None or resp.status != 200 or not isinstance(resp.body, list):
        return _unavailable("security_advisories", snap)
    return Observation(Availability.VERIFIED, len(resp.body), "direct_count",
                       ("security_advisories",),
                       "recorded only: advisories show a disclosure process as much as a weakness")


def obs_top_author_share(snap: Snapshot, as_of: datetime) -> Observation:
    commits, _, _ = _commits(snap)
    if commits is None:
        return _unavailable("commits_window", snap)
    if not commits:
        return Observation(Availability.NOT_APPLICABLE, keys=("commits_window",),
                           note="no commits in window")
    counts: dict[str, int] = {}
    for c in commits:
        counts[_author_key(c)] = counts.get(_author_key(c), 0) + 1
    return Observation(Availability.VERIFIED, round(max(counts.values()) / len(commits), 4),
                       "derived", ("commits_window",))


def obs_max_commit_window_share(snap: Snapshot, as_of: datetime, window_days: int) -> Observation:
    commits, _, _ = _commits(snap)
    if commits is None:
        return _unavailable("commits_window", snap)
    if not commits:
        return Observation(Availability.NOT_APPLICABLE, keys=("commits_window",),
                           note="no commits in window")
    dates = sorted(_commit_date(c) for c in commits)
    span, best, lo = timedelta(days=window_days), 0, 0
    for hi, d in enumerate(dates):
        while d - dates[lo] > span:
            lo += 1
        best = max(best, hi - lo + 1)
    return Observation(Availability.VERIFIED, round(best / len(dates), 4), "derived",
                       ("commits_window",), f"window of {window_days} days")


def observe_all(snap: Snapshot, m: Methodology) -> dict[str, Observation]:
    as_of = parse_ts(snap.as_of)
    burst_window = int(m.risk.get("commit_burst", {}).get("window_days", 7))
    return {
        # scored
        "commits_last_365d": obs_commits_last_365d(snap, as_of),
        "days_since_last_commit": obs_days_since_last_commit(snap, as_of),
        "releases_last_365d": obs_releases_last_365d(snap, as_of, m.ingestion.window_days),
        "community_profile_files": obs_community_profile_files(snap, as_of),
        "ci_workflows_present": obs_ci_workflows_present(snap, as_of),
        "security_policy_present": obs_security_policy_present(
            snap, as_of, m.ingestion.security_policy_paths),
        "distinct_authors_last_365d": obs_distinct_authors_last_365d(snap, as_of),
        "total_contributors": obs_total_contributors(snap, as_of),
        # signals
        "signal.stargazers_count": _repo_field("stargazers_count")(snap, as_of),
        "signal.forks_count": _repo_field("forks_count")(snap, as_of),
        "signal.subscribers_count": _repo_field("subscribers_count")(snap, as_of),
        "signal.repository_age_days": obs_repository_age_days(snap, as_of),
        "signal.published_security_advisories": obs_published_security_advisories(snap, as_of),
        "signal.top_author_share_last_365d": obs_top_author_share(snap, as_of),
        "signal.max_commit_window_share": obs_max_commit_window_share(snap, as_of, burst_window),
    }


def build_evidence(snap: Snapshot, m: Methodology, identity: ProjectIdentity) -> list[EvidenceRecord]:
    records = []
    for metric, obs in sorted(observe_all(snap, m).items()):
        cfg = m.metrics.get(metric)
        scored = cfg is not None
        normalized = (normalize(obs.value, cfg)
                      if scored and obs.availability is Availability.VERIFIED else None)
        confidence = (m.confidence.evidence_kind[obs.kind]
                      if obs.availability is Availability.VERIFIED and obs.kind else None)
        responses = [snap.get(k) for k in obs.keys if snap.get(k) is not None]
        digest = hashlib.sha256(f"{identity.project_id}|{metric}|{snap.snapshot_hash}".encode())
        records.append(EvidenceRecord(
            evidence_id=f"ev-{digest.hexdigest()[:16]}",
            project_id=identity.project_id,
            metric=metric,
            availability=obs.availability,
            evidence_kind=obs.kind,
            raw_value=obs.value,
            normalized_value=normalized,
            method=(f"{cfg.normalization}" + (f"(anchor={cfg.anchor:g})" if cfg.anchor else "")
                    if scored else "signal: recorded, not scored"),
            confidence=confidence,
            provenance=Provenance(
                source=snap.source,
                request_keys=list(obs.keys),
                endpoints=[r.endpoint for r in responses],
                response_hashes=[r.body_hash for r in responses],
                retrieved_at=snap.as_of,
            ),
            as_of=snap.as_of,
            methodology_version=m.methodology_version,
            note=obs.note,
        ))
    return records
