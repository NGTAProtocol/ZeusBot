# GHIMONEY Impact Report: NGTAProtocol/ZeusBot

> Provisional result of methodology `GHIM-IMPACT-0.2`. Weights and anchors are hypotheses. No human review was performed and this result is not used for funding.

## Summary

| Output | Value |
|---|---|
| Impact | **INSUFFICIENT_EVIDENCE**: no final Impact Score |
| Evidence Coverage | 50% |
| Confidence | 80% (base 80%, risk factor 1.00) |
| Risk | LOW (0 signal(s)) |

Impact, Coverage, Confidence and Risk are independent outputs: Coverage, Confidence and Risk never change the Impact Score.

### Why there is no Impact Score

- coverage 0.50 below minimum 0.60
- 2 core dimension(s) missing (adoption, dependency), maximum 1

## Dimensions

| Dimension | Original weight | Recalculated weight | Status | Score | Metric coverage | Confidence |
|---|---|---|---|---|---|---|
| adoption | 25% | — | NOT_AVAILABLE | — | 0% | — |
| dependency | 25% | — | INSUFFICIENT_EVIDENCE | — | 0% | — |
| maintenance | 15% | — | VERIFIED | 56.9 | 100% | 86% |
| quality | 15% | — | VERIFIED | 50.0 | 100% | 80% |
| security | 10% | — | VERIFIED | 0.0 | 100% | 60% |
| community | 10% | — | VERIFIED | 15.3 | 100% | 90% |

**Missing dimensions:** adoption, dependency. Missing dimensions are not counted as zero.

## Risk

No risk signal triggered.

A risk signal is an anomaly to be reviewed, not evidence of fraud.

## Evidence

| Metric | Availability | Raw value | Normalized | Method | Confidence | Note |
|---|---|---|---|---|---|---|
| ci_workflows_present | VERIFIED | True | 100.0 | boolean | 80% |  |
| commits_last_365d | VERIFIED | 12 | 41.3 | log_saturating(anchor=500) | 90% |  |
| community_profile_files | VERIFIED | 0.00 | 0.0 | fraction | 80% | present: none |
| days_since_last_commit | VERIFIED | 1.09 | 87.5 | log_decay(anchor=365) | 80% |  |
| distinct_authors_last_365d | VERIFIED | 1 | 17.6 | log_saturating(anchor=50) | 90% |  |
| releases_last_365d | VERIFIED | 1 | 27.0 | log_saturating(anchor=12) | 90% |  |
| security_policy_present | VERIFIED | False | 0.0 | boolean | 60% | no SECURITY.md in: SECURITY.md, .github/SECURITY.md, docs/SECURITY.md |
| signal.forks_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.max_commit_window_share | VERIFIED | 1.00 | — | signal: recorded, not scored | 80% | window of 7 days |
| signal.published_security_advisories | VERIFIED | 0 | — | signal: recorded, not scored | 90% | recorded only: advisories show a disclosure process as much as a weakness |
| signal.repository_age_days | VERIFIED | 126.14 | — | signal: recorded, not scored | 80% |  |
| signal.stargazers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.subscribers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.top_author_share_last_365d | VERIFIED | 1.00 | — | signal: recorded, not scored | 80% |  |
| total_contributors | VERIFIED | 1 | 13.1 | log_saturating(anchor=200) | 90% |  |

## Reproducibility

- Project ID: `ghp-f128c89c2f4e50b2` (GitHub repository id 1245659736)
- Methodology: `GHIM-IMPACT-0.2`, config `0.2.0`, hash `a33b51b0fb7c95b552f52066a379be6b3adf1491577d6eaed2c0e5246a6303df`
- Snapshot: `27de26b07fe55817` as of 2026-09-24T16:04:34Z, hash `27de26b07fe55817f1abeb251f1922cc7aaa4958e606bd41f04dd02309970e6d`
- Sources: github-rest-api (2022-11-28)
- Report hash: `78c9fbed70109d8bd0e96877764416cc413adf332c4b746adf0ac3e818981c7d`

Same snapshot + same methodology + same configuration produce the same report.
