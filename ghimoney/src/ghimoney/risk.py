"""Risk Engine v0.1: anomaly signals with their evidence.

A signal is an anomaly to be reviewed, never proof of fraud (Rules 10, 11).
Risk never changes the Impact Score.
"""

from __future__ import annotations

from typing import Callable

from ghimoney.methodology import Methodology
from ghimoney.models import Availability, EvidenceRecord, RiskLevel, RiskResult, RiskSignal


def _values(ev: dict[str, EvidenceRecord], *metrics: str) -> tuple[list, list[str]] | None:
    records = [ev.get(m) for m in metrics]
    if any(r is None or r.availability is not Availability.VERIFIED for r in records):
        return None
    return [r.raw_value for r in records], [r.evidence_id for r in records]


def check_popularity_vs_contributors(ev, p):
    got = _values(ev, "signal.stargazers_count", "total_contributors")
    if got is None:
        return None
    (stars, contributors), ids = got
    hit = stars >= p["min_stars"] and contributors <= p["max_contributors"]
    return hit, ids, {"stargazers_count": stars, "total_contributors": contributors}


def check_young_and_popular(ev, p):
    got = _values(ev, "signal.repository_age_days", "signal.stargazers_count")
    if got is None:
        return None
    (age, stars), ids = got
    hit = age <= p["max_age_days"] and stars >= p["min_stars"]
    return hit, ids, {"repository_age_days": age, "stargazers_count": stars}


def check_commit_burst(ev, p):
    got = _values(ev, "commits_last_365d", "signal.max_commit_window_share")
    if got is None:
        return None
    (commits, share), ids = got
    hit = commits >= p["min_commits"] and share > p["max_window_share"]
    return hit, ids, {"commits_last_365d": commits, "max_commit_window_share": share,
                      "window_days": p["window_days"]}


def check_author_concentration(ev, p):
    got = _values(ev, "commits_last_365d", "signal.top_author_share_last_365d")
    if got is None:
        return None
    (commits, share), ids = got
    hit = commits >= p["min_commits"] and share >= p["max_top_author_share"]
    return hit, ids, {"commits_last_365d": commits, "top_author_share": share}


CHECKS: dict[str, tuple[Callable, str]] = {
    "popularity_vs_contributors": (
        check_popularity_vs_contributors,
        "Popularity is disproportionate to the contributor base (possible star inflation)."),
    "young_and_popular": (
        check_young_and_popular,
        "Very young repository with high popularity (possible anomalous star growth)."),
    "commit_burst": (
        check_commit_burst,
        "Yearly activity is concentrated in a short window (possible artificial activity)."),
    "author_concentration": (
        check_author_concentration,
        "One author produced almost all recent commits (sustainability risk, not manipulation)."),
}


def assess_risk(evidence: list[EvidenceRecord], is_fork: bool | None, m: Methodology) -> RiskResult:
    ev = {e.metric: e for e in evidence}
    signals, evaluated, not_evaluated = [], [], []
    for name, (check, description) in CHECKS.items():
        params = m.risk.get(name)
        if params is None:
            continue
        outcome = check(ev, params)
        if outcome is None:
            not_evaluated.append(name)
            continue
        evaluated.append(name)
        hit, ids, observed = outcome
        if hit:
            signals.append(RiskSignal(signal_id=name, level=RiskLevel(params["level"]),
                                      description=description, evidence_ids=ids,
                                      observed=observed))

    fork_params = m.risk.get("repository_is_fork")
    if fork_params is not None:
        if is_fork is None:
            not_evaluated.append("repository_is_fork")
        else:
            evaluated.append("repository_is_fork")
            if is_fork:
                signals.append(RiskSignal(
                    signal_id="repository_is_fork", level=RiskLevel(fork_params["level"]),
                    description="Repository is a fork: impact may belong to the upstream project.",
                    evidence_ids=[], observed={"fork": True}))

    level = max((s.level for s in signals), key=lambda lv: lv.rank, default=RiskLevel.LOW)
    return RiskResult(level=level, signals=signals, checks_evaluated=evaluated,
                      checks_not_evaluated=not_evaluated)
