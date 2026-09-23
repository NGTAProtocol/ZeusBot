# GHIMONEY Impact Report: NGTAProtocol/ZeusBot

> Provisional result of methodology `GHIM-IMPACT-0.1`. Weights and anchors are hypotheses. No human review was performed and this result is not used for funding.

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

| Dimension | Weight | Effective weight | Status | Score | Metric coverage | Confidence |
|---|---|---|---|---|---|---|
| adoption | 25% | — | NOT_AVAILABLE | — | 0% | — |
| dependency | 25% | — | NOT_AVAILABLE | — | 0% | — |
| maintenance | 15% | — | VERIFIED | 55.5 | 80% | 85% |
| quality | 15% | — | VERIFIED | 0.0 | 50% | 80% |
| security | 10% | — | VERIFIED | 0.0 | 100% | 60% |
| community | 10% | — | VERIFIED | 15.3 | 100% | 90% |

Missing dimensions: adoption, dependency. Missing dimensions are not counted as zero.

## Risk

No risk signal triggered.

A risk signal is an anomaly to be reviewed, not evidence of fraud.

## Evidence

| Metric | Availability | Raw value | Normalized | Method | Confidence | Note |
|---|---|---|---|---|---|---|
| ci_workflows_present | UNKNOWN | — | — | boolean | — | no GitHub Actions workflows: CI may run on another service, so absence is not evidence of no CI |
| commits_last_365d | VERIFIED | 1 | 11.1 | log_saturating(anchor=500) | 90% |  |
| community_profile_files | VERIFIED | 0.00 | 0.0 | fraction | 80% | present: none |
| days_since_last_commit | VERIFIED | 0.01 | 99.8 | log_decay(anchor=365) | 80% |  |
| distinct_authors_last_365d | VERIFIED | 1 | 17.6 | log_saturating(anchor=50) | 90% |  |
| releases_last_365d | UNKNOWN | — | — | log_saturating(anchor=12) | — | no GitHub Releases: the project may release through tags or package registries, so absence is not evidence of zero releases |
| security_policy_present | VERIFIED | False | 0.0 | boolean | 60% | no SECURITY.md in: SECURITY.md, .github/SECURITY.md, docs/SECURITY.md |
| signal.forks_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.max_commit_window_share | VERIFIED | 1.00 | — | signal: recorded, not scored | 80% | window of 7 days |
| signal.published_security_advisories | VERIFIED | 0 | — | signal: recorded, not scored | 90% | recorded only: advisories show a disclosure process as much as a weakness |
| signal.repository_age_days | VERIFIED | 124.94 | — | signal: recorded, not scored | 80% |  |
| signal.stargazers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.subscribers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.top_author_share_last_365d | VERIFIED | 1.00 | — | signal: recorded, not scored | 80% |  |
| total_contributors | VERIFIED | 1 | 13.1 | log_saturating(anchor=200) | 90% |  |

## Reproducibility

- Project ID: `ghp-f128c89c2f4e50b2` (GitHub repository id 1245659736)
- Methodology: `GHIM-IMPACT-0.1`, config `0.1.0`, hash `cede23aedae8dd9ec033c9c9c3041466907988477b0e1f2826fbc7dae179351c`
- Snapshot: `9b966eb2d631ad45` as of 2026-09-23T11:15:16Z, hash `9b966eb2d631ad45e492a5097122bf8bcb75e1fd323b143205d6595942f36b5f`
- Sources: github-rest-api (2022-11-28)
- Report hash: `d7db9d0caee52f5691ccbee5f2dd4e626bcea2963c584a8e4faeb4e394dcfae5`

Same snapshot + same methodology + same configuration produce the same report.
