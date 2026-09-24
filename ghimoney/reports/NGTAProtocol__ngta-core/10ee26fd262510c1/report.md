# GHIMONEY Impact Report: NGTAProtocol/ngta-core

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
| maintenance | 15% | — | VERIFIED | 17.3 | 80% | 85% |
| quality | 15% | — | VERIFIED | 16.7 | 50% | 80% |
| security | 10% | — | VERIFIED | 0.0 | 100% | 60% |
| community | 10% | — | VERIFIED | 15.3 | 100% | 90% |

**Missing dimensions:** adoption, dependency. Missing dimensions are not counted as zero.

## Risk

No risk signal triggered.

A risk signal is an anomaly to be reviewed, not evidence of fraud.

## Evidence

| Metric | Availability | Raw value | Normalized | Method | Confidence | Note |
|---|---|---|---|---|---|---|
| ci_workflows_present | UNKNOWN | — | — | boolean | — | no GitHub Actions workflows: CI may run on another service, so absence is not evidence of no CI |
| commits_last_365d | VERIFIED | 2 | 17.7 | log_saturating(anchor=500) | 90% |  |
| community_profile_files | VERIFIED | 0.17 | 16.7 | fraction | 80% | present: readme |
| days_since_last_commit | VERIFIED | 133.38 | 17.0 | log_decay(anchor=365) | 80% |  |
| distinct_authors_last_365d | VERIFIED | 1 | 17.6 | log_saturating(anchor=50) | 90% |  |
| releases_last_365d | UNKNOWN | — | — | log_saturating(anchor=12) | — | no GitHub Releases: the project may release through tags or package registries, so absence is not evidence of zero releases |
| security_policy_present | VERIFIED | False | 0.0 | boolean | 60% | no SECURITY.md in: SECURITY.md, .github/SECURITY.md, docs/SECURITY.md |
| signal.forks_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.max_commit_window_share | VERIFIED | 1.00 | — | signal: recorded, not scored | 80% | window of 7 days |
| signal.published_security_advisories | NOT_AVAILABLE | — | — | signal: recorded, not scored | — | source request 'security_advisories' unavailable (HTTP 404) |
| signal.repository_age_days | VERIFIED | 133.40 | — | signal: recorded, not scored | 80% |  |
| signal.stargazers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.subscribers_count | VERIFIED | 0 | — | signal: recorded, not scored | 90% |  |
| signal.top_author_share_last_365d | VERIFIED | 1.00 | — | signal: recorded, not scored | 80% |  |
| total_contributors | VERIFIED | 1 | 13.1 | log_saturating(anchor=200) | 90% |  |

## Reproducibility

- Project ID: `ghp-e85c186c94aebdfb` (GitHub repository id 1238468046)
- Methodology: `GHIM-IMPACT-0.2`, config `0.2.0`, hash `a33b51b0fb7c95b552f52066a379be6b3adf1491577d6eaed2c0e5246a6303df`
- Snapshot: `10ee26fd262510c1` as of 2026-09-24T16:05:09Z, hash `10ee26fd262510c1009252558111ea392f5d954629ae4d93386495748e22cb0b`
- Sources: github-rest-api (2022-11-28)
- Report hash: `6069749ecedbddf3d3217a99b710cdb1ae80594af43837c240c4171ccfc75e6a`

Same snapshot + same methodology + same configuration produce the same report.
