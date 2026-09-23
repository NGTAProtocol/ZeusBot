"""Initial red-team (Directive §49): try to make the engine reward manipulation.

All scenarios use SYNTHETIC snapshots.
"""

from __future__ import annotations

from conftest import commit, make_snapshot
from ghimoney.engine import analyze


def _signals(report):
    return {s["signal_id"] for s in report["risk"]["signals"]}


def test_fake_stars_do_not_change_any_score(methodology):
    # Rule 1 / Rule 2: buying stars must not buy Impact.
    honest = analyze(make_snapshot(), methodology)
    inflated = analyze(make_snapshot(repo_fields={"stargazers_count": 250_000,
                                                  "forks_count": 40_000,
                                                  "subscribers_count": 9_000}), methodology)
    assert inflated["impact"] == honest["impact"]
    assert inflated["dimensions"] == honest["dimensions"]


def test_star_inflation_raises_risk(methodology):
    report = analyze(make_snapshot(
        {"contributors": {"status": 200, "body": [{"login": "solo"}]}},
        repo_fields={"stargazers_count": 20_000, "created_at": "2026-08-01T00:00:00Z"}),
        methodology)
    assert {"popularity_vs_contributors", "young_and_popular"} <= _signals(report)
    assert report["risk"]["level"] == "MEDIUM"


def test_commit_burst_is_flagged(methodology):
    burst = [commit(10 + i / 100, "bot") for i in range(200)]
    background = [commit(100 + i * 5, "dev") for i in range(20)]
    report = analyze(make_snapshot({"commits_window": {"status": 200,
                                                       "body": burst + background}}), methodology)
    assert "commit_burst" in _signals(report)


def _evidence(report, metric):
    return next(e for e in report["evidence"] if e["metric"] == metric)


def test_bot_author_multiplication_saturates(methodology):
    # 1,000 fake authors earn nothing over 50 real ones: the metric saturates
    # at its declared anchor (50).
    real = [commit(i, f"dev{i % 50}") for i in range(200)]
    fake = [commit(i / 10, f"bot{i}") for i in range(1000)]
    a = analyze(make_snapshot({"commits_window": {"status": 200, "body": real}}), methodology)
    b = analyze(make_snapshot({"commits_window": {"status": 200, "body": fake}}), methodology)
    ea, eb = (_evidence(r, "distinct_authors_last_365d") for r in (a, b))
    assert (ea["raw_value"], eb["raw_value"]) == (50, 1000)
    assert ea["normalized_value"] == eb["normalized_value"] == 100.0


def test_fork_is_flagged(methodology):
    assert "repository_is_fork" in _signals(analyze(make_snapshot(repo_fields={"fork": True}),
                                                    methodology))


def test_hiding_data_cannot_produce_a_score(methodology):
    # Withholding unfavourable data (making it unavailable) lowers coverage;
    # it cannot turn INSUFFICIENT_EVIDENCE into a score.
    hidden = {k: {"status": 403, "body": None}
              for k in ("commits_window", "contributors", "community_profile", "workflows")}
    report = analyze(make_snapshot(hidden), methodology)
    assert report["impact"]["score"] is None
    assert report["coverage"]["value"] < 0.5


def test_risk_signal_is_not_fraud(methodology):
    report = analyze(make_snapshot(repo_fields={"fork": True}), methodology)
    text = str(report).lower()
    assert "fraud_confirmed" not in text
    assert all(s["level"] != "CRITICAL" for s in report["risk"]["signals"])


def test_personal_data_does_not_reach_report(methodology):
    commits = [commit(1, None, "private.person@example.invalid")]
    report = analyze(make_snapshot({"commits_window": {"status": 200, "body": commits}}),
                     methodology)
    assert "private.person" not in str(report)
